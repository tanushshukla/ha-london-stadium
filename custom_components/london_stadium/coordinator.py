"""Data coordinator for the London Stadium integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    LondonStadiumApiClient,
    LondonStadiumApiClientCommunicationError,
    LondonStadiumApiClientResponseError,
)
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class LondonStadiumDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate London Stadium API updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        api_client: LondonStadiumApiClient,
    ) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=1),
        )
        self.api_client = api_client

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the website."""
        try:
            return await self.api_client.async_get_next_event()
        except (
            LondonStadiumApiClientCommunicationError,
            LondonStadiumApiClientResponseError,
        ) as err:
            raise UpdateFailed(str(err)) from err
