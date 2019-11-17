import unittest

from mopidy_soundcloud import Extension


class ExtensionTest(unittest.TestCase):
    def test_get_default_config(self):
        ext = Extension()

        config = ext.get_default_config()

        self.assertIn("[soundcloud]", config)
        self.assertIn("enabled = True", config)

    def test_get_config_schema(self):
        ext = Extension()

        schema = ext.get_config_schema()

        self.assertIn("auth_token", schema)
        self.assertIn("explore_songs", schema)
