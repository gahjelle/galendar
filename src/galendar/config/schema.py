from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, HttpUrl, SecretStr


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PathConfig(StrictModel):
    cache: Path


class LogConfig(StrictModel):
    level: (
        Literal["trace"]
        | Literal["debug"]
        | Literal["info"]
        | Literal["warning"]
        | Literal["error"]
    )
    format: str


class DropboxConfig(StrictModel):
    client_key: str
    client_secret: SecretStr
    client_token: SecretStr
    auth_url: HttpUrl
    token_url: HttpUrl
    token_path: Path
    cache_timeout: int


class GalendarConfig(StrictModel):
    paths: PathConfig
    log: LogConfig
    dropbox: DropboxConfig
