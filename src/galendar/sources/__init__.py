"""Sources to interact with."""

import pyplugs

PACKAGE = str(__package__)


def read_file(source: str, file_name: str, *, fresh: bool = False) -> str:
    """Read a file from the source."""
    return pyplugs.call_typed(
        PACKAGE,
        plugin=source,
        func="read_file",
        _return_type=str(),  # noqa: UP018
        file_name=file_name,
        fresh=fresh,
    )


def write_file(source: str, file_name: str, *, content: str) -> None:
    """Write a file into a source."""
    return pyplugs.call_typed(
        PACKAGE,
        plugin=source,
        func="write_file",
        _return_type=None,
        file_name=file_name,
        content=content,
    )
