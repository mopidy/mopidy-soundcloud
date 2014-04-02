from __future__ import unicode_literals

import os

from mopidy import ext, config
from mopidy.exceptions import ExtensionError


__version__ = '1.2.3'
__url__ = 'https://github.com/mopidy/mopidy-soundcloud'


class SoundCloudExtension(ext.Extension):

    dist_name = 'Mopidy-SoundCloud'
    ext_name = 'soundcloud'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(SoundCloudExtension, self).get_config_schema()
        schema['explore_songs'] = config.Integer()
        schema['auth_token'] = config.Secret()
        schema['explore'] = config.Deprecated()
        schema['explore_pages'] = config.Deprecated()
        return schema

    def validate_config(self, config):
        if not config.getboolean('soundcloud', 'enabled'):
            return
        if not config.get('soundcloud', 'auth_token'):
            raise ExtensionError(
                'In order to use SoundCloud extension you must provide an '
                'auth token. For more information referrer to '
                'https://github.com/mopidy/mopidy-soundcloud/')

    def setup(self, registry):
        from .actor import SoundCloudBackend
        registry.add('backend', SoundCloudBackend)
