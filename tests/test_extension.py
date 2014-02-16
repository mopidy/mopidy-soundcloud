from __future__ import unicode_literals

import unittest

from mopidy_soundcloud import SoundCloudExtension


class ExtensionTest(unittest.TestCase):

    def test_get_default_config(self):
        ext = SoundCloudExtension()

        config = ext.get_default_config()

        self.assertIn('[soundcloud]', config)
        self.assertIn('enabled = True', config)

    def test_get_config_schema(self):
        ext = SoundCloudExtension()

        schema = ext.get_config_schema()

        self.assertIn('auth_token', schema)
        self.assertIn('explore_songs', schema)
