# Home Assistant London Stadium

Custom Home Assistant integration for London Stadium events.

This integration scrapes the public London Stadium events page directly and exposes the next event as a sensor entity.

## Current entity

- `sensor.london_stadium_next_event`

State:
- next event date

Attributes:
- `event_name`
- `event_day`
- `start_date`
- `url`
- `image`
- `more_info_url`
- `image_url`
- `timestamp`

The integration fetches data from:

```text
https://www.london-stadium.com/events/index.html
```

## Install manually

Copy `custom_components/london_stadium` into your Home Assistant `custom_components` directory:

```text
config/custom_components/london_stadium
```

Restart Home Assistant, then add the integration from the UI. No extra API service or URL is required.
