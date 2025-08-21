"""Interact with Dropbox files."""

import contextlib
import json
from collections.abc import Generator
from datetime import datetime, timedelta

import dropbox
import dropbox.files
import requests

from galendar.config import config
from galendar.console import console
from galendar.log import logger
from galendar.sources import cache

cfg = config.dropbox


def read_file(
    file_name: str, *, fresh: bool = False, not_exist_ok: bool = False
) -> str:
    """Read a file from Dropbox or cache."""
    content = cache.read_file(file_name, timeout=cfg.cache_timeout)
    if fresh or not content:
        if not_exist_ok and file_name not in list_files():
            logger.debug(f"{file_name} is not available in Dropbox")
            return ""

        with dropbox_auth() as dbx:
            logger.debug(f"Downloading {file_name} from Dropbox")
            _, response = dbx.files_download(f"/{file_name}")
            content = response.text
            cache.write_file(file_name, content=content)
    return content


def write_file(file_name: str, content: str) -> None:
    """Write a file to Dropbox and cache."""
    with dropbox_auth() as dbx:
        logger.debug(f"Writing {file_name} to Dropbox")
        # TODO(gahjelle): Use update as WriteMode to handle conflicts better.
        # Need to track rev in cache as well.
        dbx.files_upload(
            content.encode("utf-8"),
            f"/{file_name}",
            mode=dropbox.files.WriteMode("overwrite"),
        )
        cache.write_file(file_name, content=content)


def list_files() -> list[str]:
    """List files available in Dropbox."""
    with dropbox_auth() as dbx:
        return [file.name for file in dbx.files_list_folder("").entries]


@contextlib.contextmanager
def dropbox_auth() -> Generator[dropbox.Dropbox]:
    """Authenticate with Dropbox."""
    token = get_access_token()
    with dropbox.Dropbox(oauth2_access_token=token) as dbx:
        yield dbx


def initialize_auth() -> None:
    """Do the first initialization of the auth process."""
    auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(
        cfg.client_key,
        cfg.client_secret.get_secret_value(),
        token_access_type="offline",  # noqa: S106
    )

    authorize_url = auth_flow.start()
    console.print(f"1. Go to: {authorize_url}")
    console.print("2. Click 'Allow' (you might have to log in first).")
    console.print("3. Copy the authorization code.")
    auth_code = input("Enter the authorization code: ").strip()

    try:
        auth_result = auth_flow.finish(auth_code)
    except requests.HTTPError as err:
        logger.critical(f"Authentication error: {err}")
        raise SystemExit(1) from None

    tokens = {
        "access_token": auth_result.access_token,
        "refresh_token": auth_result.refresh_token,
        "expires_at": auth_result.expires_at.isoformat(),
    }
    config.paths.dropbox_token.write_text(json.dumps(tokens), encoding="utf-8")


def get_access_token() -> str:
    """Get a valid access token."""
    if not config.paths.dropbox_token.exists():
        initialize_auth()

    tokens = json.loads(config.paths.dropbox_token.read_text(encoding="utf-8"))

    if not is_expired(tokens["expires_at"]):
        return str(tokens["access_token"])

    refresh_tokens(tokens["refresh_token"])
    return get_access_token()


def is_expired(expires_at: str) -> bool:
    """Check if an expires_at timestamp has expired."""
    expire_dt = datetime.fromisoformat(expires_at).astimezone(config.timezone)
    return expire_dt < datetime.now(tz=config.timezone) + timedelta(seconds=10)


def refresh_tokens(refresh_token: str) -> None:
    """Get a fresh authorization token."""
    logger.debug("Refreshing the Dropbox token")

    # sourcery skip: use-named-expression
    response = requests.post(
        str(cfg.token_url),
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": cfg.client_key,
            "client_secret": cfg.client_secret.get_secret_value(),
        },
        timeout=cfg.requests_timeout,
    )

    if response:
        fresh = response.json()
        tokens = {
            "access_token": fresh["access_token"],
            "refresh_token": refresh_token,
            "expires_at": (
                datetime.now(tz=config.timezone)
                + timedelta(seconds=fresh["expires_in"])
            ).isoformat(),
        }
        config.paths.dropbox_token.write_text(json.dumps(tokens), encoding="utf-8")
    else:
        response.raise_for_status()
