"""Sensor platform for the London Stadium integration."""

from __future__ import annotations

from datetime import date

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_TITLE, DOMAIN, SOURCE_URL
from .coordinator import LondonStadiumDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the London Stadium sensor from a config entry."""
    coordinator: LondonStadiumDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([LondonStadiumNextEventSensor(coordinator, entry.entry_id)])


class LondonStadiumNextEventSensor(
    CoordinatorEntity[LondonStadiumDataUpdateCoordinator], SensorEntity
):
    """Represent the next London Stadium event."""

    _attr_has_entity_name = True
    _attr_name = "Next Event"
    _attr_icon = "mdi:stadium"
    _attr_device_class = SensorDeviceClass.DATE

    def __init__(
        self,
        coordinator: LondonStadiumDataUpdateCoordinator,
        entry_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_next_event"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=DEFAULT_TITLE,
            manufacturer="London Stadium",
            model="Events",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url=SOURCE_URL,
        )

    @property
    def native_value(self) -> date | None:
        """Return the next event date."""
        event_day = self.coordinator.data.get("eventDay")
        if not event_day:
            return None

        try:
            return date.fromisoformat(event_day)
        except ValueError:
            return None

    @property
    def extra_state_attributes(self) -> dict[str, str | None]:
        """Return event metadata."""
        data = self.coordinator.data
        return {
            "event_name": data.get("name"),
            "event_day": data.get("eventDay"),
            "start_date": data.get("startDate"),
            "url": data.get("moreInfoUrl"),
            "image": data.get("imageUrl"),
            "more_info_url": data.get("moreInfoUrl"),
            "image_url": data.get("imageUrl"),
            "timestamp": data.get("timestamp"),
        }
