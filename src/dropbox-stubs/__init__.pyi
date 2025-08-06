from datetime import datetime
from types import TracebackType
from typing import Literal, Self

class FileMetadata: ...

class Response:
    text: str

class Dropbox:
    def __init__(self, oauth2_access_token: str) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...
    def files_download(self, path: str) -> tuple[FileMetadata, Response]: ...
    def files_upload(self, f: bytes, path: str) -> FileMetadata: ...

class OAuth2FlowNoRedirectResult:
    access_token: str
    refresh_token: str
    expires_at: datetime

class DropboxOAuth2FlowNoRedirect:
    def __init__(
        self,
        consumer_key: str,
        consumer_secret: str,
        token_access_type: Literal["offline", "online"],
    ) -> None: ...
    def start(self) -> str: ...
    def finish(self, code: str) -> OAuth2FlowNoRedirectResult: ...
