# coding=utf-8
from __future__ import unicode_literals

import unittest

import pykka

from mopidy_soundcloud import SoundCloudExtension, actor
from mopidy_soundcloud.library import (
    SoundCloudLibraryProvider, new_folder, simplify_search_query)
from mopidy_soundcloud.soundcloud import safe_url


class ApiTest(unittest.TestCase):
    def setUp(self):
        config = SoundCloudExtension().get_config_schema()
        config['auth_token'] = '1-35204-61921957-55796ebef403996'
        # using this user http://maildrop.cc/inbox/mopidytestuser
        self.backend = actor.SoundCloudBackend.start(
            config={'soundcloud': config, 'proxy': {}},
            audio=None
        ).proxy()
        self.library = SoundCloudLibraryProvider(backend=self.backend)

    def tearDown(self):
        pykka.ActorRegistry.stop_all()

    def test_add_folder(self):
        try:
            from mopidy.models import Ref
        except ImportError as e:
            self.skipTest(e.message)
        self.assertEquals(
            new_folder('Test', ['test']),
            Ref(name='Test', type='directory',
                uri='soundcloud:directory:test')
        )

    def test_mpc_search(self):
        self.assertEquals(
            simplify_search_query({u'any': [u'explosions in the sky']}),
            'explosions in the sky'
        )

    def test_moped_search(self):
        self.assertEquals(
            simplify_search_query(
                {
                    u'track_name': [u'explosions in the sky'],
                    u'any': [u'explosions in the sky']
                }
            ),
            'explosions in the sky explosions in the sky'
        )

    def test_simple_search(self):
        self.assertEquals(
            simplify_search_query('explosions in the sky'),
            'explosions in the sky'
        )

    def test_aria_search(self):
        self.assertEquals(
            simplify_search_query(['explosions', 'in the sky']),
            'explosions in the sky'
        )

    def test_only_resolves_soundcloud_uris(self):
        self.assertIsNone(self.library.search(
            {'uri': 'http://www.youtube.com/watch?v=wD6H6Yhluo8'}))

    def test_returns_url_safe_string(self):
        self.assertEquals(
            safe_url('Alternative/Indie/rock/pop '),
            'Alternative%2FIndie%2Frock%2Fpop+')
        self.assertEquals(
            safe_url('D∃∃P Hau⑀ iNDiE DᴬNCE | №➊ ²⁰¹⁴'),
            'DP+Hau+iNDiE+DANCE+%7C+No+2014')

    def test_default_folders(self):
        try:
            from mopidy.models import Ref
        except ImportError as e:
            self.skipTest(e.message)
        self.assertEquals(
            self.library.browse('soundcloud:directory'),
            [
                Ref(name='Following', type='directory',
                    uri='soundcloud:directory:following'),
                Ref(name='Liked', type='directory',
                    uri='soundcloud:directory:liked'),
                Ref(name='Sets', type='directory',
                    uri='soundcloud:directory:sets'),
                Ref(name='Stream', type='directory',
                    uri='soundcloud:directory:stream')
            ]
        )
