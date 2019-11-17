import unittest
from unittest import mock

from mopidy_soundcloud.soundcloud import cache


class CacheTest(unittest.TestCase):
    def test_decorator(self):
        func = mock.Mock()
        decorated_func = cache()
        decorated_func(func)
        func()
        assert func.called is True
        assert decorated_func._call_count == 1

    def test_set_default_cache(self):
        @cache()
        def returnstring():
            return "ok"

        assert returnstring() == "ok"

    def test_set_ttl_cache(self):
        func = mock.Mock()
        decorated_func = cache(func, ttl=5)
        func()
        assert func.called is True
        assert decorated_func._call_count == 1
        assert decorated_func.ttl == 5
