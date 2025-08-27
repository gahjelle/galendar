"""Use Pydantic to define the configuration schema."""

from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, HttpUrl, SecretStr


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PathConfig(StrictModel):
    cache: Path
    data: Path
    dropbox_token: Path


class FilesConfig(StrictModel):
    events: str
    birthdays: str


class LogConfig(StrictModel):
    level: Literal["trace", "debug", "info", "success", "warning", "error"]
    template: str


class DropboxConfig(StrictModel):
    client_key: str
    client_secret: SecretStr
    client_token: SecretStr
    auth_url: HttpUrl
    token_url: HttpUrl
    requests_timeout: int
    cache_timeout: int


class GalendarConfig(StrictModel):
    timezone: ZoneInfo
    paths: PathConfig
    files: FilesConfig
    log: LogConfig
    dropbox: DropboxConfig
