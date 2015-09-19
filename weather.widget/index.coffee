# Config such as API keys and binary locations are in weather.conf
# Arguments for fetching the weather, like location both provided and autodetected and reverse geocoding
# are in fetch-forecast.args, one per line. Run fetch-forecast.py -h to see the available arguments.
command: """weather.widget/fetch-forecast.py 2>/dev/null --config-file="weather.widget/weather.conf" @weather.widget/fetch-forecast.args"""

refreshFrequency: 1800000

render: (o) -> """
  <div class="today">
    <div class="location"></div>
    <div class="date"></div>
    <div class="icon"></div>
    <div class="temp"></div>
    <div class="summary">
        <div class="currently"></div>
        <div class="conditions"></div>
    </div>
  </div>
  <div class="forecast"></div>
  <div class="updated"></div>
  """

update: (output, domEl) ->
  return if not output
  try
    data = JSON.parse(output)
  catch
    return
  today = data.daily.data[0]
  currently = data.currently
  daily = data.daily
  date = @getDate today.time

  $domEl = $(domEl)

  $domEl.find('.location').text data.formatted_location
  $domEl.find('.date').text @dayMapping[date.getDay()]
  $domEl.find('.temp').html """
    <span class='hi'>#{Math.round(today.temperatureMax)}°</span> /
    <span class='lo'>#{Math.round(today.temperatureMin)}°</span>
  """

  $domEl.find('.currently').text currently.summary + ' and ' + Math.round(currently.temperature) +
    '°, feels like ' + Math.round(currently.apparentTemperature) + '°.'
  $domEl.find('.conditions').text today.summary
  $domEl.find('.icon')[0].innerHTML = @getIcon(currently)

  forecastEl = $domEl.find('.forecast').html('')
  forecastEl.append """<div class="outlook">#{daily.summary}</div>"""
  for day in data.daily.data[1..5]
    forecastEl.append @renderForecast(day)

  $domEl.find('.updated').text 'Updated at ' + @formatTimestamp()

renderForecast: (data) ->
  date = @getDate data.time

  """
    <div class='entry'>
      <div class='icon'>#{@getIcon data}</div>
      <div class='temp'>#{Math.round(data.temperatureMax)}°</div>
      <div class='day'>#{@dayMapping[date.getDay()][0..2]}</div>
      <div class='temp'>#{Math.round(data.temperatureMin)}°</div>
    </div>
  """

formatTimestamp: (date) ->
  date = new Date() if not date

  pad = (s) ->
      ('0' + s).slice(-2)

  [date.getHours(), pad(date.getMinutes()), pad(date.getSeconds())].join ':'

style: """
  bottom: 20%
  left: 50%
  color: #fff
  font-family: Helvetica Neue
  text-align: center
  width: 360px
  margin-left: -180px

  @font-face
    font-family Weather
    src url(weather.widget/icons.svg) format('svg')

  .today
    display: inline-block
    text-align: left
    position: relative

  .icon
    font-family: Weather
    font-size: 50px
    line-height: 70px
    position: absolute
    left: 0
    top: 0
    vertical-align: middle

  .temp, .date, .location
    padding-left: 90px

  .date, .location
    font-size: 11px
    margin-bottom: 5px

  .temp
    font-weight: 200
    font-size: 32px

    .hi
      color: #fff

    .lo
      color: #fafafa

  .summary
    font-size: 14px
    text-align: center
    line-height: 1.5
    color: #fff
    margin-top: 20px

  .forecast
    margin-top: 15px
    padding-top: 10px
    border-top: 1px solid #fff

  .forecast .outlook
    margin-bottom: 10px
    font-size: 11px

  .forecast .entry
    display: inline-block
    margin-right: 40px
    text-align: center

    div
      margin-top: 5px

    &:last-child
      margin-right: 0;

    .temp
      font-size: 12px
      padding: 0

    .icon
      font-size: 15px
      line-height: 20px
      position: static

    .day
      font-size: 12px

  .updated
    text-align: right
    font-size: 10px
    margin-top: 10px
"""

dayMapping:
  0: 'Sunday'
  1: 'Monday'
  2: 'Tuesday'
  3: 'Wednesday'
  4: 'Thursday'
  5: 'Friday'
  6: 'Saturday'

iconMapping:
  "rain"                :"&#xf019;"
  "snow"                :"&#xf01b;"
  "fog"                 :"&#xf014;"
  "cloudy"              :"&#xf013;"
  "wind"                :"&#xf021;"
  "clear-day"           :"&#xf00d;"
  "mostly-clear-day"    :"&#xf00c;"
  "partly-cloudy-day"   :"&#xf002;"
  "clear-night"         :"&#xf02e;"
  "partly-cloudy-night" :"&#xf031;"
  "unknown"             :"&#xf03e;"

getIcon: (data) ->
  return @iconMapping['unknown'] unless data
  if data.icon.indexOf('cloudy') > -1
    if data.cloudCover < 0.25
      @iconMapping["clear-day"]
    else if data.cloudCover < 0.5
      @iconMapping["mostly-clear-day"]
    else if data.cloudCover < 0.75
      @iconMapping["partly-cloudy-day"]
    else
      @iconMapping["cloudy"]
  else
    @iconMapping[data.icon]

getDate: (utcTime) ->
  date  = new Date(0)
  date.setUTCSeconds(utcTime)
  date
