"""Load Galendar configuration."""

import configaroo
import platformdirs

from galendar.config.schema import GalendarConfig

path = configaroo.find_pyproject_toml() / "galendar.toml"
config = (
    configaroo.Configuration.from_file(path)
    .add_envs(
        {
            "GALENDAR_LOG_LEVEL": "log.level",
            "DROPBOX_CLIENT_KEY": "dropbox.client_key",
            "DROPBOX_CLIENT_SECRET": "dropbox.client_secret",
            "DROPBOX_CLIENT_TOKEN": "dropbox.client_token",
        }
    )
    .parse_dynamic({"__init__.cache_path": platformdirs.user_cache_dir("galendar")})
    .with_model(model=GalendarConfig)
)
