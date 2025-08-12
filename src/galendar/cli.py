"""CLI for Galendar."""

from datetime import datetime, timedelta

import configaroo
import typer

from galendar import log
from galendar.calendar import Calendar
from galendar.config import config
from galendar.console import console
from galendar.formats import gcal
from galendar.log import logger
from galendar.sources import dropbox

app = typer.Typer()

TODAY = datetime.now(tz=config.timezone).date().isoformat()

options = {
    "start_date": typer.Option(TODAY, "--date", "-d", help="First date shown"),
    "num_weeks": typer.Option(3, "--num-weeks", "-n", help="Number of weeks to cover"),
    "fresh": typer.Option(
        False, "--fresh-data", "-f", help="Fetch fresh data from Dropbox"
    ),
    "full_year": typer.Option(False, "--show-year", "-y", help="Show the full year"),
}


@app.callback()
def main(log_level: str = config.log.level) -> None:
    """Geir Arne's Dropbox backed calendar."""
    log.init(level=log_level)


@app.command()
def show_config() -> None:
    """Show the configuration."""
    configaroo.print_configuration(config)


@app.command()
def show(
    start_date: datetime = options["start_date"],
    num_weeks: int = options["num_weeks"],
    full_year: bool = options["full_year"],
    fresh: bool = options["fresh"],
) -> None:
    """Show the current calendar."""
    start_date = start_date.astimezone(tz=config.timezone)
    end_date = start_date + timedelta(days=num_weeks * 7 - start_date.weekday())
    if full_year:
        start_date = start_date.replace(month=1, day=1)
        end_date = start_date.replace(year=start_date.year + 1)
    logger.debug(f"Time range: {start_date} - {end_date}")

    num_days = (end_date - start_date).days
    years = {d.year for d in [start_date + timedelta(days=n) for n in range(num_days)]}
    diaries = "\n".join(
        dropbox.read_file(diary_name, fresh=fresh, not_exist_ok=True)
        for diary_name in [f"diary{year}.txt" for year in years]
    )
    calendar = Calendar(gcal.parse(diaries))
    for event in calendar.filter(start=start_date, end=end_date):
        console.print(str(event))


@app.command()
def add(start_date: datetime = options["start_date"]) -> None:
    """Add an event to the calendar."""


@app.command()
def tui() -> None:
    """Open the calendar TUI."""
