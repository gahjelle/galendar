"""Calendar class."""

from dataclasses import dataclass
from datetime import datetime

from galendar.config import config

TODAY = datetime.now(tz=config.timezone)


@dataclass(order=True)
class Event:
    """Calendar events."""

    start: datetime
    description: str
    location: str
    active: bool = True

    def __str__(self) -> str:
        """Represent an event in the console."""
        color = "red" if self.is_today() else "white" if self.active else "grey39"
        return f"[{color}]{self.start:%a %Y-%m-%d}   {self.description}[/]"

    def is_today(self) -> bool:
        """Check if event happens today."""
        return (
            TODAY.year == self.start.year
            and TODAY.month == self.start.month
            and TODAY.day == self.start.day
        )


@dataclass
class Calendar:
    """Calendar consisting of events."""

    events: list[Event]

    def filter(self, start: datetime, end: datetime) -> list[Event]:
        """Get a subset of the calendar.

        The list of events will be sorted by the start times.
        """
        return sorted(event for event in self.events if start <= event.start < end)
