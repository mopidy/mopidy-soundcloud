from __future__ import unicode_literals

import os
from mopidy import ext, config
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

**Default config**

.. code-block:: ini

"""

__version__ = '1.0.13'


class SoundCloudExtension(ext.Extension):

    dist_name = 'Mopidy-SoundCloud'
    ext_name = 'soundcloud'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(SoundCloudExtension, self).get_config_schema()
        schema['explore'] = config.List()
        schema['explore_pages'] = config.Integer()
        schema['auth_token'] = config.Secret()
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
