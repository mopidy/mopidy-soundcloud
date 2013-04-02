from __future__ import unicode_literals

from mopidy import ext
from mopidy.exceptions import ExtensionError
from mopidy.utils import config, formatting


default_config = """
[soundcloud]
enabled = True

# Your SoundCloud auth token, you can get yours at http://www.mopidy.com/authenticate
auth_token = 

# Extra playlists from http://www.soundcloud.com/explore
explore = pop/Easy Listening, rock/Indie, electronic/Ambient

# Number of pages (which roughly translates to hours) to fetch
explore_pages = 1
"""

__doc__ = """A extension for playing music from SoundCloud.

This extension handles URIs starting with ``soundcloud:`` and enables you,
to play music from SoundCloud web service.

See https://github.com/dz0ny/mopidy-soundcloud/ for further instructions on
using this extension.

**Issues:**

https://github.com/dz0ny/mopidy-soundcloud/issues

**Dependencies:**

requests

**Default config**

.. code-block:: ini

%(config)s
""" % {'config': formatting.indent(default_config)}

__version__ = '1.0.9'


class SoundCloudExtension(ext.Extension):

    dist_name = 'Mopidy-SoundCloud'
    ext_name = 'soundcloud'
    version = __version__

    def get_default_config(self):
        return default_config

    def get_config_schema(self):
        schema = config.ExtensionConfigSchema()
        schema['explore'] = config.List()
        schema['explore_pages'] = config.Integer()
        schema['auth_token'] = config.String(required=True, secret=True)
        return schema

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
