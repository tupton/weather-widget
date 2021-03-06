# Weather Forecast Widget
Made for [Übersicht][u]

  [u]: http://tracesof.net/uebersicht/

![The widget in action](https://raw.githubusercontent.com/tupton/weather-widget/master/screenshot.png)

## Notes

Weather is fetched with the `fetch-forecast.py` script. There is a config file for this script in
`weather.conf`, and the script is called by the `command` in `index.coffee` with the arguments in
`fetch-forecast.args`.

Run `./fetch-forecast.py -h` to see a list of available arguments.

`weather.conf` is the config file where your forecast.io API key and, optionally, your Google
geocoding API key live. Rename the example config and replace the values with your own API keys.

 * [Forecast.io API key][fapi]
 * [Google Geocoding API key][gapi]

  [fapi]: https://developer.forecast.io.
  [gapi]: https://developers.google.com/maps/documentation/geocoding/?csw=1#api_key

### Location And Auto-detection

If you install the [`whereami` script][w], you can automatically get your latitude and longitude to
use when fetching weather. The location of this script is configured in `weather.conf`.

  [w]: https://github.com/robmathers/WhereAmI

If need to enter your latitude and longitude coordinates, which you can find
using [Google Maps][gm], you provide them with the `--latlon` option in `fetch-forecast.args`.

  [gm]: https://www.google.com/maps

You can also enter a human-readable location with the `--location` argument in
`fetch-forecast.args`.

### Reverse Geocoding

If you use location auto-detection, it's useful to print the location name in the weather summary.
The [Google Geocoding API][geocode] is used to determine a place name from the given latitude and
longitude coordinates. If you do not wish to use this feature or you do not have a geocoding API
key, you can omit the `--geocode` option from the arguments in `fetch-forecast.args`.

  [geocode]: https://developers.google.com/maps/documentation/geocoding/

## Credits

Icons by [Erik Flowers][ef].

  [ef]: http://erikflowers.github.io/weather-icons/

Based heavily on the [original widget][o] by [Felix Hageloh][fh].

  [o]: https://github.com/felixhageloh/weather-widget
  [fh]: http://tracesof.net/
