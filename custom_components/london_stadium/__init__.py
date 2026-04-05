"""The London Stadium integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import LondonStadiumApiClient
from .const import DEFAULT_TITLE, DOMAIN
from .coordinator import LondonStadiumDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up London Stadium from a config entry."""
    api_client = LondonStadiumApiClient(session=async_get_clientsession(hass))
    coordinator = LondonStadiumDataUpdateCoordinator(hass, api_client)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate older entries that stored an external API URL."""
    if entry.version > 2:
        return False

    if entry.version == 1:
        hass.config_entries.async_update_entry(
            entry,
            title=DEFAULT_TITLE,
            data={},
            unique_id=DOMAIN,
            version=2,
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
