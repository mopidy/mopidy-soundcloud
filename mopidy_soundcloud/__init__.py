from __future__ import unicode_literals

import mopidy
from mopidy import ext
from mopidy.exceptions import ExtensionError
from .actor import SoundCloudBackend

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

- :attr:`mopidy.settings.SOUNDCLOUD_AUTH_TOKEN`
- :attr:`mopidy.settings.SOUNDCLOUD_EXPLORE`
"""

__version__ = '1.0'


class SoundCloudExtension(ext.Extension):

    name = 'Mopidy-SoundCloud'
    version = __version__

    def get_default_config(self):
        return """[soundcloud]
        auth_key = False
        explore = "pop,indie"
        """

    def validate_config(self, config):
        if not config.get('auth_token', False):
            raise ExtensionError("In order to use SoundCloud extension you\
             must provide auth_token, for more information referrer to \
             https://github.com/dz0ny/mopidy-soundcloud/")

    def validate_environment(self):
        try:
            import requests  # noqa
        except ImportError as e:
            raise ExtensionError('Library requests not found', e)

    def get_backend_classes(self):
        return [SoundCloudBackend]
