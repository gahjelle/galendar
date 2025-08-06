"""Sources to interact with."""

import pyplugs

PACKAGE = str(__package__)


def read_file(source: str, file_name: str, *, fresh: bool = False) -> str:
    """Read a file from the source."""
    return pyplugs.call(
        PACKAGE, plugin=source, func="read_file", file_name=file_name, fresh=fresh
    )


def write_file(source: str, file_name: str, content: str) -> None:
    """Write a file into a source."""
    return pyplugs.call(
        PACKAGE, plugin=source, func="write_file", file_name=file_name, content=content
    )
