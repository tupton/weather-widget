#! /usr/local/bin/python

"""
Fetch forecast from forecast.io for a given latitude and longitude. Optionally reverse geocode a
place name for the location and include it in the json response.
"""

from __future__ import print_function

import os
import argparse
import ConfigParser
import requests
import json

def reverse_geocode(latitude, longitude, config):
    geocode_key = config.get('googlegeocode', 'api_key')
    geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json'
    geocode_params = {'key': geocode_key, 'latlng': '%s,%s' % (latitude, longitude), 'sensor': False, 'result_type': 'neighborhood|locality'}

    req = requests.get(geocode_url, params=geocode_params)
    result = req.json()

    results = result.get('results', [])

    if len(results) == 0:
        return ''

    formatted = results[0].get('formatted_address', '')
    trimmed = ','.join(formatted.split(',')[:-2])
    return trimmed

def fetch_forecast(latitude, longitude, config, geocode=False):
    forecast_key = config.get('forecastio', 'api_key')
    forecast_url = "https://api.forecast.io/forecast/%(api_key)s/%(latitude)s,%(longitude)s" % {'api_key': forecast_key, 'latitude': latitude, 'longitude': longitude}
    forecast_params = {'units': 'auto', 'exclude': 'minutely,hourly,alerts,flags'}

    req = requests.get(forecast_url, params=forecast_params)
    forecast = req.json()

    if geocode is True:
        location = reverse_geocode(latitude, longitude, config)
        forecast['formatted_location'] = location

    return forecast

if __name__ == "__main__":
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('latitude', help="The latitude of the location to fetch forecast for")
    parser.add_argument('longitude', help="The longitude of the location to fetch forecast for")
    parser.add_argument('--geocode', '-g', action='store_true', help="If provided, reverse geocode the given location and include it in the JSON forecast")

    args = parser.parse_args()

    config = ConfigParser.SafeConfigParser()
    config_file = os.path.join(__location__, 'fetch-forecast.conf')
    config.read(config_file)

    response = fetch_forecast(args.latitude, args.longitude, config, geocode=args.geocode)
    print(json.dumps(response))
