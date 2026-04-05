"""Client for scraping London Stadium events directly from the website."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

from aiohttp import ClientError, ClientSession
from bs4 import BeautifulSoup, Tag

from .const import SOURCE_URL

SOURCE_TIMEZONE = ZoneInfo("Europe/London")
REQUEST_HEADERS = {
    "accept": "text/html,application/xhtml+xml",
    "user-agent": "Mozilla/5.0 (compatible; london-stadium-home-assistant/1.0)",
}


class LondonStadiumApiClientError(Exception):
    """Base error for the API client."""


class LondonStadiumApiClientCommunicationError(LondonStadiumApiClientError):
    """Error raised for network issues."""


class LondonStadiumApiClientResponseError(LondonStadiumApiClientError):
    """Error raised for invalid responses."""


def _normalize_whitespace(value: str) -> str:
    """Collapse repeated whitespace into single spaces."""
    return " ".join(value.split())


def _get_attr(element: Tag | None, name: str) -> str | None:
    """Read and trim an HTML attribute."""
    if element is None:
        return None

    value = element.get(name)
    if not value:
        return None

    return value.strip()


def _get_text(element: Tag | None) -> str | None:
    """Read and normalize element text."""
    if element is None:
        return None

    text = _normalize_whitespace(element.get_text(" ", strip=True))
    return text or None


def _make_absolute_url(url: str | None) -> str | None:
    """Normalize a possibly relative URL against the source page."""
    if not url:
        return None

    return urljoin(SOURCE_URL, url)


def _extract_name(card: Tag) -> str | None:
    """Extract the event name from a card."""
    name_element = card.select_one(".event-card__name[itemprop='name']")
    if name_element is not None:
        return _get_text(name_element)

    for candidate in reversed(card.select("[itemprop='name']")):
        name = _get_text(candidate) or _get_attr(candidate, "content")
        if name:
            return name

    return None


def _extract_event(card: Tag) -> dict[str, Any] | None:
    """Parse a single event card."""
    start_date = _get_attr(card.select_one("[itemprop='startDate']"), "content")
    event_day = start_date[:10] if start_date else None
    name = _extract_name(card)

    if not name or not event_day:
        return None

    timestamp = _get_text(card.select_one(".event-card__timestamp"))
    more_info_url = _make_absolute_url(
        _get_attr(card.select_one("a[itemprop='url']"), "href")
    )
    image_url = _make_absolute_url(
        _get_attr(card.select_one(".event-card__image"), "content")
        or _get_attr(card.select_one("img"), "src")
    )

    return {
        "name": name,
        "eventDay": event_day,
        "startDate": start_date,
        "timestamp": timestamp,
        "moreInfoUrl": more_info_url,
        "imageUrl": image_url,
    }


def _sort_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort events by start date, matching the old scraper behavior."""

    def _sort_key(event: dict[str, Any]) -> tuple[int, str]:
        start_date = event.get("startDate")
        if not start_date:
            return (1, event["name"])

        return (0, start_date)

    return sorted(events, key=_sort_key)


def _parse_events(html: str) -> list[dict[str, Any]]:
    """Extract event cards from the events listing page."""
    soup = BeautifulSoup(html, "html.parser")
    events = [
        event
        for card in soup.select(".event-card[itemtype='http://schema.org/Event']")
        if (event := _extract_event(card)) is not None
    ]
    return _sort_events(events)


class LondonStadiumApiClient:
    """Client for the London Stadium website."""

    def __init__(self, session: ClientSession) -> None:
        self._session = session

    async def async_get_events(self) -> list[dict[str, Any]]:
        """Fetch and parse all listed events."""
        try:
            async with self._session.get(SOURCE_URL, headers=REQUEST_HEADERS) as response:
                if response.status != 200:
                    raise LondonStadiumApiClientResponseError(
                        f"Unexpected page status: {response.status}"
                    )

                html = await response.text()
        except ClientError as err:
            raise LondonStadiumApiClientCommunicationError(
                "Error communicating with the London Stadium website"
            ) from err

        events = _parse_events(html)
        if not events:
            raise LondonStadiumApiClientResponseError(
                "London Stadium events page did not contain any event cards"
            )

        return events

    async def async_get_next_event(self) -> dict[str, Any]:
        """Return the next upcoming event, if one exists."""
        events = await self.async_get_events()
        today_in_london = datetime.now(SOURCE_TIMEZONE).date().isoformat()

        return next(
            (event for event in events if event["eventDay"] >= today_in_london),
            {},
        )
