"""Load galendar configuration."""

from importlib import resources

import platformdirs
from configaroo import Configuration

from galendar.config.schema import GalendarConfig

with resources.path("galendar.config", "galendar.toml") as path:
    config = Configuration.from_file(
        path,
        extra_dynamic={"__init__.cache_path": platformdirs.user_cache_dir("galendar")},
        envs={
            "GALENDAR_LOG_LEVEL": "log.level",
            "DROPBOX_CLIENT_KEY": "dropbox.client_key",
            "DROPBOX_CLIENT_SECRET": "dropbox.client_secret",
            "DROPBOX_CLIENT_TOKEN": "dropbox.client_token",
        },
    ).with_model(model=GalendarConfig)
