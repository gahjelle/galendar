"""Parse a gcal file into a list of calendar events."""

from collections.abc import Iterator
from datetime import datetime, time, timedelta
from types import SimpleNamespace

import parse

from galendar.calendar import Event
from galendar.config import config

DATE_FMT = "%Y%m%d"

description_patterns = [
    parse.compile("{start_time:%H:%M} {_} @ {location}, m {_}"),
    parse.compile("{start_time:%H:%M} {_} @ {location}"),
    parse.compile("{start_time:%H:%M} {_}"),
    parse.compile("{_} @ {location}, m {_}"),
    parse.compile("{_} @ {location}"),
    parse.compile("{_}"),
]


def parse(file: str) -> list[Event]:
    """Parse a gcal file."""
    return [event for line in file.splitlines() for event in parse_line(line)]


def parse_line(line: str) -> Iterator[Event]:
    """Parse one line in a gcal file."""
    date_str, _, description = line.partition("\t")
    if not any(
        (parts := pattern.parse(description.removeprefix("--")))
        for pattern in description_patterns
    ):
        parts = SimpleNamespace(named={})
    start_time = parts.named.get("start_time", time(0, 0))
    location = parts.named.get("location", "")

    for date in _convert_to_dates(date_str):
        yield Event(
            start=date + timedelta(hours=start_time.hour, minutes=start_time.minute),
            description=description,
            location=location,
            active=not description.startswith("--"),
        )


def _convert_to_dates(date_str: str) -> Iterator[datetime]:
    """Convert a gcal date string into one or more Python datetimes."""
    start_date_str, _, suffix = date_str.partition("#")
    end_date_str = start_date_str[: -len(suffix)] + suffix if suffix else start_date_str
    end_date = datetime.strptime(end_date_str, DATE_FMT).astimezone(tz=config.timezone)

    date = datetime.strptime(start_date_str, DATE_FMT).astimezone(tz=config.timezone)
    while date <= end_date:
        yield date
        date += timedelta(days=1)
