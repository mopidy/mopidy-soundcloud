import pathlib

import pkg_resources

from mopidy import config, ext
from mopidy.exceptions import ExtensionError

__version__ = pkg_resources.get_distribution("Mopidy-SoundCloud").version


class Extension(ext.Extension):

    dist_name = "Mopidy-SoundCloud"
    ext_name = "soundcloud"
    version = __version__

    def get_default_config(self):
        return config.read(pathlib.Path(__file__).parent / "ext.conf")

    def get_config_schema(self):
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
            raise ExtensionError(
                "In order to use SoundCloud extension you must provide an "
                "auth token. For more information refer to "
                "https://github.com/mopidy/mopidy-soundcloud/"
            )

    def setup(self, registry):
        from .actor import SoundCloudBackend

        registry.add("backend", SoundCloudBackend)
