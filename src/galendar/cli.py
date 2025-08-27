"""CLI for Galendar."""

import calendar
from datetime import datetime, timedelta

import configaroo
import typer
from logaroo import logger

from galendar.calendar import Calendar
from galendar.config import config
from galendar.console import console
from galendar.formats import gcal
from galendar.sources import cache, dropbox

app = typer.Typer()

NOW = datetime.now(tz=config.timezone)
TODAY = NOW.date()
YESTERDAY = TODAY - timedelta(days=1)
MONDAY = TODAY - timedelta(days=TODAY.weekday())

options = {
    "start_date": typer.Option(
        YESTERDAY.isoformat(), "--date", "-d", help="First date shown"
    ),
    "num_weeks": typer.Option(3, "--num-weeks", "-n", help="Number of weeks to cover"),
    "show_cal": typer.Option(False, "--show-cal", "-c", help="Show monthly calendars"),
    "search": typer.Option("", "--search", "-s", help="Phrase to search for"),
    "all_time": typer.Option(
        False, "--all-time", "-a", help="Show events from all time"
    ),
    "full_month": typer.Option(False, "--show-month", "-m", help="Show the full month"),
    "full_year": typer.Option(False, "--show-year", "-y", help="Show the full year"),
    "fresh": typer.Option(
        False, "--fresh-data", "-f", help="Fetch fresh data from Dropbox"
    ),
}


@app.callback()
def main(log_level: str = config.log.level) -> None:
    """Geir Arne's Dropbox backed calendar."""
    logger.level = log_level
    logger.template = config.log.template


@app.command()
def show_config(
    section: str | None = typer.Argument(
        None, help="Show a section of the configuration"
    ),
) -> None:
    """Show the configuration."""
    configaroo.print_configuration(config, section=section)


@app.command()
def show(  # noqa: PLR0913
    start_date: datetime = options["start_date"],
    num_weeks: int = options["num_weeks"],
    show_cal: bool = options["show_cal"],
    search: str = options["search"],
    full_year: bool = options["full_year"],
    full_month: bool = options["full_month"],
    all_time: bool = options["all_time"],
    fresh: bool = options["fresh"],
) -> None:
    """Show the current calendar."""
    start_date = start_date.astimezone(tz=config.timezone)
    end_date = start_date + timedelta(days=num_weeks * 7 - start_date.weekday())
    if full_month:
        start_date = start_date.replace(day=1)
        end_date = (start_date + timedelta(days=31)).replace(day=1)
    if full_year:
        start_date = start_date.replace(month=1, day=1)
        end_date = start_date.replace(year=start_date.year + 1)
    if all_time:
        start_date = datetime(2014, 1, 1, tzinfo=config.timezone)

    logger.debug(f"Time range: [green]{start_date.date()} - {end_date.date()}[/]")

    num_days = (end_date - start_date).days
    years = sorted(
        {d.year for d in [start_date + timedelta(days=n) for n in range(num_days)]}
    )
    diaries = "\n".join(
        dropbox.read_file(diary_name, fresh=fresh, not_exist_ok=True)
        for diary_name in [config.files.events.format(year=year) for year in years]
    )
    events = Calendar(gcal.parse(diaries))

    console.print(f"[blue]{NOW.strftime('%A, %-d %B %Y, %H:%M')}[/]\n")
    year, month = 0, 0
    for event in events.filter(start=start_date, end=end_date):
        if search.lower() not in event.description.lower():
            continue
        if show_cal and (year, month) != (event.start.year, event.start.month):
            year, month = event.start.year, event.start.month
            console.print("\n" + calendar.month(year, month))
        console.print(str(event))


@app.command()
def add(
    date: str = typer.Argument(help="Date of event"),
    description: str = typer.Argument(help="Description of event"),
) -> None:
    """Add an event to the calendar."""
    logger.info(f"Adding event: {date} {description}")
    diary_name = config.files.events.format(year=date[:4])
    events = dropbox.read_file(diary_name, fresh=True, not_exist_ok=True).split("\n")
    dropbox.write_file(
        diary_name, "\n".join(sorted([f"{date}\t{description}", *events]))
    )


@app.command()
def upload(year: int = typer.Argument(help="Year file to upload")) -> None:
    """Upload a calendar file."""
    diary_name = config.files.events.format(year=year)
    if content := cache.read_file(diary_name):
        dropbox.write_file(diary_name, content)


@app.command()
def tui() -> None:
    """Open the calendar TUI."""
