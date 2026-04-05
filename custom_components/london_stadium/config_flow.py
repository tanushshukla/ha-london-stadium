"""Config flow for the London Stadium integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    LondonStadiumApiClient,
    LondonStadiumApiClientCommunicationError,
    LondonStadiumApiClientResponseError,
)
from .const import DEFAULT_TITLE, DOMAIN


async def _validate_input(hass) -> dict[str, Any]:
    """Validate that we can reach and parse the events page."""
    client = LondonStadiumApiClient(session=async_get_clientsession(hass))
    await client.async_get_next_event()
    return {"title": DEFAULT_TITLE}


class LondonStadiumConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for London Stadium."""

    VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            try:
                info = await _validate_input(self.hass)
            except LondonStadiumApiClientCommunicationError:
                errors["base"] = "cannot_connect"
            except LondonStadiumApiClientResponseError:
                errors["base"] = "invalid_response"
            except Exception:
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=info["title"],
                    data={},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            errors=errors,
        )
