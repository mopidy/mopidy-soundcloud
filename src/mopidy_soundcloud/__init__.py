import pathlib
from importlib.metadata import version

from mopidy import config, ext
from mopidy.exceptions import ExtensionError

__version__ = version("mopidy-soundcloud")


class Extension(ext.Extension):
    dist_name = "mopidy-soundcloud"
    ext_name = "soundcloud"
    version = __version__

    def get_default_config(self) -> str:
        return config.read(pathlib.Path(__file__).parent / "ext.conf")

    def get_config_schema(self) -> config.ConfigSchema:
        schema = super().get_config_schema()
        schema["explore_songs"] = config.Integer(optional=True)
        schema["auth_token"] = config.Secret()
        schema["explore"] = config.Deprecated()
        schema["explore_pages"] = config.Deprecated()
        return schema

    def validate_config(self, config):  # no_coverage
        if not config.getboolean("soundcloud", "enabled"):
            return
        if not config.get("soundcloud", "auth_token"):
            msg = (
                "In order to use SoundCloud extension you must provide an "
                "auth token. For more information refer to "
                "https://github.com/mopidy/mopidy-soundcloud/"
            )
            raise ExtensionError(msg)

    def setup(self, registry: ext.Registry) -> None:
        from .actor import SoundCloudBackend  # noqa: PLC0415

        registry.add("backend", SoundCloudBackend)
