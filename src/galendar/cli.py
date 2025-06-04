"""CLI for Galendar"""

from datetime import date, datetime, timedelta

import rich
import typer

from galendar import log
from galendar.config import config
from galendar.log import logger

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
    "log_level": typer.Option(
        config.log.default_level, "--log-level", help="Level for logging"
    ),
}


def init(log_level: str = config.log.default_level):
    """Initializations common to several commands"""
    log.init(level=log_level)


@app.command()
def show_config():
    """Show the configuration"""
    console.print(config)


@app.command()
def show(
    start_date: datetime = options["start_date"](TODAY),
    num_weeks: int = options["num_weeks"](3),
    log_level: str = options["log_level"],
):
    """Show the current calendar"""
    init(log_level=log_level)

    end_date = start_date + timedelta(days=num_weeks * 7 - start_date.weekday())
    logger.info(f"{start_date = } {end_date = }")

    from galendar.sources import dropbox

    file_name = "diary.txt"

    print(dropbox.read_file(file_name))
