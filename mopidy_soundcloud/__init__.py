from __future__ import unicode_literals

from mopidy import ext
from mopidy.exceptions import ExtensionError

__doc__ = """A extension for playing music from SoundCloud.

This extension handles URIs starting with ``soundcloud:`` and enables you,
to play music from SoundCloud web service.

See https://github.com/dz0ny/mopidy-soundcloud/ for further instructions on
using this extension.

**Issues:**

https://github.com/dz0ny/mopidy-soundcloud/issues

**Dependencies:**

requests

**Settings:**

- :attr:`mopidy.settings.auth_token`
- :attr:`mopidy.settings.explore`
"""

__version__ = '1.0.0'


class SoundCloudExtension(ext.Extension):

    name = 'Mopidy-SoundCloud'
    version = __version__

    def get_default_config(self):
        return """[ext.soundcloud]
        enabled = True
        auth_key = False
        explore = "pop,indie"
        """

    def validate_config(self, config):
        if not config.getboolean('soundcloud', 'enabled'):
            return
        if not config.get('soundcloud', 'auth_token'):
            raise ExtensionError("In order to use SoundCloud extension you\
             must provide auth_token, for more information referrer to \
             https://github.com/dz0ny/mopidy-soundcloud/")

    def validate_environment(self):
        try:
            import requests  # noqa
        except ImportError as e:
            raise ExtensionError('Library requests not found', e)

    def get_backend_classes(self):
        from .actor import SoundCloudBackend
        return [SoundCloudBackend]
