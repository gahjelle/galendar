"""Parse a gcal file into a list of calendar events."""

import functools
import re
from collections.abc import Iterator
from datetime import datetime, time, timedelta

from galendar.calendar import Event
from galendar.config import config

DATE_FMT = "%Y%m%d"


@functools.cache
def get_description_patterns() -> list[re.Pattern[str]]:
    """Get regex patterns that can grab information from descriptions."""
    start_time = r"(?P<start_time>[0-9]{1,2}:[0-9]{2})"
    location = r"(?P<location>.+?)"
    return [
        re.compile(rf"^{start_time} (.+?) @ {location}, m (.+)$"),
        re.compile(rf"^{start_time} (.+?) @ {location}$"),
        re.compile(rf"^{start_time} (.+)$"),
        re.compile(rf"^(.+?) @ {location}, m (.+)$"),
        re.compile(rf"^(.+?) @ {location}$"),
        re.compile(r"^(.+)$"),
    ]


def parse(file: str) -> list[Event]:
    """Parse a gcal file."""
    return [event for line in file.splitlines() for event in parse_line(line)]


def parse_line(line: str) -> Iterator[Event]:
    """Parse one line in a gcal file."""
    date_str, _, description = line.partition("\t")

    parts: dict[str, str] = {}
    for pattern in get_description_patterns():
        if m := pattern.match(description.removeprefix("--")):
            parts = m.groupdict()
            break

    start_hour, _, start_minute = parts.get("start_time", "0:00").partition(":")
    start_time = time(int(start_hour), int(start_minute))
    location = parts.get("location", "")

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
