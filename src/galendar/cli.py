"""CLI for Galendar"""

from datetime import date, datetime, timedelta

import configaroo
import rich
import typer

from galendar import log
from galendar.calendar import Calendar
from galendar.config import config
from galendar.formats import gcal
from galendar.log import logger
from galendar.sources import dropbox

app = typer.Typer()
console = rich.console.Console()

TODAY = date.today().isoformat()

options = {
    "start_date": lambda start_date: typer.Option(
        start_date, "--date", "-d", help="First date shown"
    ),
    "num_weeks": lambda num_weeks: typer.Option(
        num_weeks, "--num-weeks", "-n", help="Number of weeks to cover"
    ),
    "fresh": typer.Option(
        False, "--fresh-data", "-f", help="Fetch fresh data from Dropbox"
    ),
    "full_year": typer.Option(False, "--show-year", "-y", help="Show the full year"),
}


@app.callback()
def main(log_level: str = config.log.level):
    """Geir Arne's Dropbox backed calendar"""
    log.init(level=log_level)


@app.command()
def show_config():
    """Show the configuration"""
    configaroo.print_configuration(config)


@app.command()
def show(
    start_date: datetime = options["start_date"](TODAY),
    num_weeks: int = options["num_weeks"](3),
    full_year: bool = options["full_year"],
    fresh: bool = options["fresh"],
):
    """Show the current calendar"""
    end_date = start_date + timedelta(days=num_weeks * 7 - start_date.weekday())
    if full_year:
        start_date = start_date.replace(month=1, day=1)
        end_date = start_date.replace(year=start_date.year + 1)
    logger.debug(f"Time range: {start_date} - {end_date}")

    diaries = "\n".join(
        dropbox.read_file(diary_name, fresh=fresh)
        for diary_name in ["diary.txt"]  # , "diary2024.txt"]
    )
    calendar = Calendar(gcal.parse(diaries))
    for event in calendar.filter(start=start_date, end=end_date):
        console.print(str(event))
