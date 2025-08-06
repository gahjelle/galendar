"""Handle logging with Loguru."""

import sys

from loguru import logger

from galendar.config import config

__all__ = ["init", "logger"]


def init(level: str = config.log.level) -> None:
    """Initialize the logger."""
    logger.remove()
    logger.add(sys.stderr, level=level.upper(), format=config.log.format)
