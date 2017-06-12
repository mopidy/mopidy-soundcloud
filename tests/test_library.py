# coding=utf-8
from __future__ import unicode_literals

import unittest

import mock

from mopidy_soundcloud import SoundCloudExtension
from mopidy_soundcloud.library import (
    SoundCloudLibraryProvider,
    new_folder,
    simplify_search_query
)
from mopidy_soundcloud.soundcloud import safe_url


class LibraryTest(unittest.TestCase):
    def setUp(self):
        config = SoundCloudExtension().get_config_schema()
        config['auth_token'] = '1-35204-61921957-55796ebef403996'
        # using this user http://maildrop.cc/inbox/mopidytestuser
        self.backend = mock.Mock()
        self.library = SoundCloudLibraryProvider(backend=self.backend)

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

    def test_lookup_explore(self):
        self.library.lookup('soundcloud:directory:explore/0')
        self.backend.remote.get_explore.assert_called_once_with('0')

    def test_lookup_following(self):
        self.library.lookup('soundcloud:directory:following')
        self.backend.remote.get_followings.assert_called_once_with()

    def test_lookup_groups(self):
        self.library.lookup('soundcloud:directory:groups/0')
        self.backend.remote.get_groups.assert_called_once_with('0')

    def test_lookup_liked(self):
        self.library.lookup('soundcloud:directory:liked')
        self.backend.remote.get_user_liked.assert_called_once_with()

    def test_lookup_sets(self):
        self.library.lookup('soundcloud:directory:sets/0')
        self.backend.remote.get_set.assert_called_once_with('0')

    def test_lookup_stream(self):
        self.library.lookup('soundcloud:directory:stream')
        self.backend.remote.get_user_stream.assert_called_once_with()

    def test_lookup_track(self):
        self.library.lookup('sc:something')
        self.backend.remote.resolve_url.assert_called_once_with('something')

    def test_lookup_track_by_id(self):
        self.backend.remote.parse_track_uri.return_value = 0
        self.backend.remote.get_track.return_value = 'bar'
        result = self.library.lookup('foo')
        self.backend.remote.parse_track_uri.assert_called_once_with('foo')
        self.backend.remote.get_track.assert_called_once_with(0)
        self.assertEquals(result, ['bar'])

    def test_lookup_error(self):
        self.backend.remote.get_user_stream.side_effect = Exception('No.')
        result = self.library.lookup('soundcloud:directory:stream')
        self.assertEquals(result, [])
