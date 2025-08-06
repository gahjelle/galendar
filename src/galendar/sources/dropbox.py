"""Interact with Dropbox files"""

import contextlib
import json
from datetime import datetime, timedelta

import dropbox
import requests

from galendar.config import config
from galendar.log import logger
from galendar.sources import cache

cfg = config.dropbox


def read_file(file_name: str, fresh: bool = False) -> str:
    """Read a file from Dropbox or cache"""
    content = cache.read_file(file_name, timeout=cfg.cache_timeout)
    if fresh or not content:
        with dropbox_auth() as dbx:
            logger.info(f"Downloading {file_name} from Dropbox")
            _, response = dbx.files_download(f"/{file_name}")
            content = response.text
            cache.write_file(file_name, content=content)
    return content


def write_file(file_name: str, content: str) -> None:
    """Write a file to Dropbox and cache"""
    with dropbox_auth() as dbx:
        logger.info(f"Writing {file_name} to Dropbox")
        dbx.files_upload(content.encode("utf-8"), f"/{file_name}")
        cache.write_file(file_name, content=content)


@contextlib.contextmanager
def dropbox_auth():
    token = get_access_token()
    with dropbox.Dropbox(oauth2_access_token=token) as dbx:
        yield dbx


def initialize_auth() -> None:
    """Do the first initialization of the auth process"""
    auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(
        cfg.client_key,
        cfg.client_secret.get_secret_value(),
        token_access_type="offline",
    )

    authorize_url = auth_flow.start()
    print(f"1. Go to: {authorize_url}")
    print("2. Click 'Allow' (you might have to log in first).")
    print("3. Copy the authorization code.")
    auth_code = input("Enter the authorization code: ").strip()

    try:
        auth_result = auth_flow.finish(auth_code)
    except Exception as err:
        logger.critical(f"Authentication error: {err}")
        raise SystemExit(1) from None

    tokens = {
        "access_token": auth_result.access_token,
        "refresh_token": auth_result.refresh_token,
        "expires_at": auth_result.expires_at.isoformat(),
    }
    cfg.token_path.write_text(json.dumps(tokens), encoding="utf-8")


def get_access_token():
    if not cfg.token_path.exists():
        initialize_auth()

    tokens = json.loads(cfg.token_path.read_text(encoding="utf-8"))

    if not is_expired(tokens["expires_at"]):
        return tokens["access_token"]

    refresh_tokens(tokens["refresh_token"])
    return get_access_token()


def is_expired(expires_at):
    """Check if an expires_at timestamp has expired"""
    return datetime.fromisoformat(expires_at) < datetime.now() + timedelta(seconds=10)


def refresh_tokens(refresh_token: str):
    """Get a fresh authorization token"""
    logger.info("Refreshing the Dropbox token")
    response = requests.post(
        str(cfg.token_url),
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": cfg.client_key,
            "client_secret": cfg.client_secret.get_secret_value(),
        },
    )

    if response.status_code == 200:
        fresh = response.json()
        tokens = {
            "access_token": fresh["access_token"],
            "refresh_token": refresh_token,
            "expires_at": (
                datetime.now() + timedelta(seconds=fresh["expires_in"])
            ).isoformat(),
        }
        cfg.token_path.write_text(json.dumps(tokens), encoding="utf-8")
    else:
        response.raise_for_status()
