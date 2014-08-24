#! /usr/local/bin/python

"""
Fetch forecast from forecast.io for a given latitude and longitude. Optionally reverse geocode a
place name for the location and include it in the json response.
"""

from __future__ import print_function

import sys
import argparse
import ConfigParser
import requests
import json
import subprocess

class GeocodeError(Exception):
    pass

class LocationError(Exception):
    pass

def _make_geocode_request(params, config):
    geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json'

    try:
        geocode_key = config.get('googlegeocode', 'api_key')
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError) as e:
        raise GeocodeError('Invalid or nonexistent Google geocode API key: %s' % (e,))

    params.setdefault('key', geocode_key)

    req = requests.get(geocode_url, params=params)
    result = req.json()

    status = result.get('status', '')
    if status != 'OK':
        raise GeocodeError(result.get('error_message', 'Bad geocode request: %s' % (params,)))

    return result.get('results', [])

def geocode(location, config):
    geocode_params = {'address': location}
    results = _make_geocode_request(geocode_params, config)

    if len(results) == 0:
        raise GeocodeError('Unable to geocode the location: %s' % (location,))

    latlon = results[0].get('geometry', {}).get('location', {})
    return (latlon.get('lat', ''), latlon.get('lng', ''))

def reverse_geocode(latitude, longitude, config):
    geocode_params = {'latlng': '%s,%s' % (latitude, longitude), 'sensor': False, 'result_type': 'neighborhood|locality'}
    results = _make_geocode_request(geocode_params, config)

    if len(results) == 0:
        raise GeocodeError('Unable to reverse geocode the location: %s, %s' % (latitude, longitude))

    formatted = results[0].get('formatted_address', '')
    trimmed = ','.join(formatted.split(',')[:-2])
    return trimmed

def fetch_forecast(latitude, longitude, config, reverse_geocode_location=False):
    forecast_key = config.get('forecastio', 'api_key')
    forecast_url = "https://api.forecast.io/forecast/%(api_key)s/%(latitude)s,%(longitude)s" % {'api_key': forecast_key, 'latitude': latitude, 'longitude': longitude}
    forecast_params = {'units': 'auto', 'exclude': 'minutely,hourly,alerts,flags'}

    req = requests.get(forecast_url, params=forecast_params)
    forecast = req.json()

    location = ''
    if reverse_geocode_location:
        try:
            location = reverse_geocode(latitude, longitude, config)
        except GeocodeError as e:
            print(e, file=sys.stderr)

    forecast['formatted_location'] = location

    return forecast

def detect_location(args, config):
    if not args.auto_detect_location:
        raise LocationError('The option to auto-detect a location was not provided.')

    whereami = config.get('autodetect', 'whereami')
    proc = subprocess.Popen(whereami, stdout=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    if proc.returncode == 0:
        # Successful output looks like:
        #
        #    Latitude: 30.264673
        #    Longitude: -97.733859
        #    Accuracy (m): 65.000000
        #    Timestamp: 2014-08-24, 17:25:25 CDT
        return tuple(l[1].strip() for l in [tuple(line.split(':', 1)) for line in stdout.split('\n')][:2])

    raise LocationError('Detecting a location failed: %s' % (stdout,)) # whereami still prints to stdout if there's an error

def get_location_from_args(args, config):
    if args.latlon:
        try:
            lat, lon = (l.strip() for l in args.latlon.split(','))
        except ValueError as e:
            raise LocationError('Invalid latitude and longitude coordinates: %s\n%s' % (args.latlon, e))

    elif args.location:
        try:
            lat, lon = geocode(args.location, config)
        except GeocodeError as e:
            raise LocationError('Invalid location: %s\n%s' % (args.location, e))

    return (lat, lon)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, fromfile_prefix_chars='@')

    parser.add_argument('--auto-detect-location', action='store_true', help="If provided, attempt to detect the location with the `whereami` script, the location of which is provided in a config file.")
    parser.add_argument('--reverse-geocode', action='store_true', help="If provided, reverse geocode the given location and include it in the JSON forecast. If you provide a human-readable location, this option is ignored and that location is used in the output.")
    parser.add_argument('--config-file', '-c', default='weather.conf', help="The file to use for config options, including the forecast.io and Google geocode API keys.")

    location_group = parser.add_mutually_exclusive_group()
    location_group.add_argument('--latlon', help="The comma-separated latitude and longitude of the location to fetch forecast for")
    location_group.add_argument('--location', help="A human-readable location that will be geocoded and used as the location to fetch forecast for")

    args = parser.parse_args()

    config = ConfigParser.SafeConfigParser()
    config.read(args.config_file)

    try:
        try:
            lat, lon = detect_location(args, config)
        except Exception as e:
            print('Unable to detect location: %s' % (e,), file=sys.stderr)
            lat, lon = get_location_from_args(args, config)
    except LocationError as e:
        print('Unable to determine a location to request forecast for: %s', e)
        sys.exit(1)

    response = fetch_forecast(lat, lon, config, reverse_geocode_location=args.reverse_geocode)
    print(json.dumps(response))
