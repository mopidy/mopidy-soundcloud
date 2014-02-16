from __future__ import unicode_literals
from mock import Mock

import unittest

from mopidy_soundcloud.soundcloud import cache


class CacheTest(unittest.TestCase):

    def test_decorator(self):
        func = Mock()
        decorated_func = cache()
        decorated_func(func)
        func()
        self.assertEquals(func.called, True)
        self.assertEquals(decorated_func._call_count, 1)

    def test_set_default_cache(self):

        @cache()
        def returnstring():
            return 'ok'

        self.assertEquals(returnstring(), 'ok')

    def test_set_ttl_cache(self):

        func = Mock()
        decorated_func = cache(func, ttl=5)
        func()
        self.assertEquals(func.called, True)
        self.assertEquals(decorated_func._call_count, 1)
        self.assertEquals(decorated_func.ttl, 5)
