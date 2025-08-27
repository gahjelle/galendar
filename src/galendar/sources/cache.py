"""Interact with cache."""

import time

from logaroo import logger

from galendar.config import config


def read_file(
    file_name: str, *, fresh: bool = False, not_exist_ok: bool = False, timeout: int = 0
) -> str:
    """Read a file from cache."""
    logger.trace(f"{not_exist_ok = } is ignored for cache")

    path = config.paths.cache / file_name
    if not path.exists() or fresh:
        return ""
    if timeout and time.time() - path.stat().st_mtime > timeout:
        return ""
    logger.debug(
        f"Read [green]{file_name}[/] from cache ([green]{config.paths.cache}[/])"
    )
    return path.read_text(encoding="utf-8")


def write_file(file_name: str, content: str) -> None:
    """Write a file into cache."""
    path = config.paths.cache / file_name
    path.parent.mkdir(parents=True, exist_ok=True)

    logger.debug(
        f"Write [green]{file_name}[/] to cache ([green]{config.paths.cache}[/])"
    )
    path.write_text(content, encoding="utf-8")
