import sys

from loguru import logger

from galendar.config import config

cfg = config.log


def init(level: str = cfg.default_level):
    """Initialize the logger"""
    logger.remove()
    logger.add(sys.stderr, level=level.upper(), format=cfg.format)
