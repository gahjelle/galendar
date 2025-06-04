"""Sources to interact with"""

from pathlib import Path
from typing import Iterator

import pyplugs

PACKAGE = __package__ or ""


def read_file(source: str, file_name: str, fresh: bool = False) -> Iterator[Path]:
    """Read a file from the source"""
    return pyplugs.call(
        PACKAGE, plugin=source, func="read_file", file_name=file_name, fresh=fresh
    )


def write_file(source: str, file_name: str, content: str) -> Iterator[Path]:
    """Write a file into a source"""
    return pyplugs.call(
        PACKAGE, plugin=source, func="write_file", file_name=file_name, content=content
    )
