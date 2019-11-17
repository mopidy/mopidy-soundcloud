import unittest

from mopidy_soundcloud import Extension


class ExtensionTest(unittest.TestCase):
    def test_get_default_config(self):
        ext = Extension()

        config = ext.get_default_config()

        assert "[soundcloud]" in config
        assert "enabled = True" in config

    def test_get_config_schema(self):
        ext = Extension()

        schema = ext.get_config_schema()

        assert "auth_token" in schema
        assert "explore_songs" in schema
