# Home Assistant London Stadium

Custom Home Assistant integration for London Stadium events.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=tanushshukla&category=integration&repository=ha-london-stadium)

This integration scrapes the public London Stadium events page directly and exposes the next event as a sensor entity.

## Install with HACS

1. Open HACS in Home Assistant.
2. Go to the integrations section.
3. Open the menu, choose `Custom repositories`, and add `https://github.com/tanushshukla/ha-london-stadium`.
4. Select category `Integration`.
5. Find `London Stadium` in HACS and install it.
6. Restart Home Assistant, then add the integration from the UI.

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
