"""Parse a gcal file into a list of calendar events"""

from datetime import datetime, time, timedelta
from types import SimpleNamespace
from typing import Iterator

from parse import compile

from galendar.calendar import Event

DATE_FMT = "%Y%m%d"

description_patterns = [
    compile("{start_time:%H:%M} {_} @ {location}, m {_}"),
    compile("{start_time:%H:%M} {_} @ {location}"),
    compile("{start_time:%H:%M} {_}"),
    compile("{_} @ {location}, m {_}"),
    compile("{_} @ {location}"),
    compile("{_}"),
]


def parse(file: str) -> list[Event]:
    """Parse a gcal file"""
    return [event for line in file.splitlines() for event in parse_line(line)]


def parse_line(line: str) -> Iterator[Event]:
    """Parse one line in a gcal file"""
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
    """Convert a gcal date string into one or more Python datetimes"""
    start_date_str, _, suffix = date_str.partition("#")
    end_date_str = start_date_str[: -len(suffix)] + suffix if suffix else start_date_str
    end_date = datetime.strptime(end_date_str, DATE_FMT)

    date = datetime.strptime(start_date_str, DATE_FMT)
    while date <= end_date:
        yield date
        date += timedelta(days=1)
