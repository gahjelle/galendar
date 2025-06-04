from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, HttpUrl


class StrictConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PathConfig(StrictConfig):
    cache: Path


class LogConfig(StrictConfig):
    default_level: (
        Literal["trace"]
        | Literal["debug"]
        | Literal["info"]
        | Literal["warning"]
        | Literal["error"]
    )
    format: str


class DropboxConfig(StrictConfig):
    client_key: str
    client_secret: str
    client_token: str
    auth_url: HttpUrl
    token_url: HttpUrl
    token_path: Path
    cache_timeout: int


class GalendarConfig(StrictConfig):
    paths: PathConfig
    log: LogConfig
    dropbox: DropboxConfig
