from __future__ import unicode_literals

import os

from mopidy import config, ext
from mopidy.exceptions import ExtensionError


__version__ = '2.0.2'


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
        schema['http_max_retries'] = config.Integer()
        return schema

    def validate_config(self, config):  # no_coverage
        if not config.getboolean('soundcloud', 'enabled'):
            return
        if not config.get('soundcloud', 'auth_token'):
            raise ExtensionError(
                'In order to use SoundCloud extension you must provide an '
                'auth token. For more information refer to '
                'https://github.com/mopidy/mopidy-soundcloud/')

    def setup(self, registry):
        from .actor import SoundCloudBackend
        registry.add('backend', SoundCloudBackend)
