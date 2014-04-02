from __future__ import unicode_literals

import unittest
from mopidy.models import Track
from mopidy_soundcloud import SoundCloudExtension

from mopidy_soundcloud.soundcloud import SoundCloudClient


class ApiTest(unittest.TestCase):

    def setUp(self):
        config = SoundCloudExtension().get_config_schema()
        config['auth_token'] = '1-35204-61921957-55796ebef403996'
        # using this user http://maildrop.cc/inbox/mopidytestuser
        self.api = SoundCloudClient(config)

    def test_resolves_string(self):
        id = self.api.parse_track_uri('soundcloud:song.38720262')
        self.assertEquals(id, '38720262')

    def test_resolves_object(self):

        trackc = {}
        trackc[b'uri'] = 'soundcloud:song.38720262'
        track = Track(**trackc)

        id = self.api.parse_track_uri(track)
        self.assertEquals(id, '38720262')

    def test_resolves_emptyTrack(self):

        track = self.api.get_track('s38720262')
        self.assertIsInstance(track, Track)
        self.assertEquals(track.uri, None)

    def test_resolves_Track(self):

        track = self.api.get_track('38720262')
        self.assertIsInstance(track, Track)
        self.assertEquals(
            track.uri,
            'soundcloud:song/Burial Four Tet - Nova.38720262'
        )

    def test_resolves_http_url(self):

        track = self.api.resolve_url(
            'https://soundcloud.com/swedensfinestmusicblog/'
            'robert-parker-brooklyn-brigde'
        )[0]
        self.assertIsInstance(track, Track)
        self.assertEquals(
            track.uri,
            'soundcloud:song/Robert Parker - Brooklyn Brigde.135101951'
        )

    def test_get_user_liked(self):

        tracks = self.api.get_user_liked()
        self.assertIsInstance(tracks, list)

    def test_get_user_stream(self):

        tracks = self.api.get_user_stream()
        self.assertIsInstance(tracks, list)

    def test_get_explore(self):

        tracks = self.api.get_explore()
        self.assertIsInstance(tracks, list)
        self.assertEquals(tracks[0], 'Popular+Music')

    def test_get_explore_popular_music(self):

        tracks = self.api.get_explore('1')
        self.assertIsInstance(tracks, list)
        self.assertIsInstance(tracks[0], Track)

    def test_get_followings(self):

        tracks = self.api.get_followings()
        self.assertIsInstance(tracks, list)

    def test_get_sets(self):

        tracks = self.api.get_sets()
        self.assertIsInstance(tracks, list)

    def test_get_groups(self):

        tracks = self.api.get_groups()
        self.assertIsInstance(tracks, list)

    def test_get_group_tracks(self):

        tracks = self.api.get_groups(136)
        self.assertIsInstance(tracks[0], Track)

    def test_safe_url(self):

        self.assertEquals('Barsuk Records',
                          self.api.safe_url('"@"Barsuk      Records'))
        self.assertEquals('_Barsuk Records',
                          self.api.safe_url('_Barsuk \'Records\''))

    def test_resolves_stream_Track(self):

        track = self.api.get_track('38720262', True)
        self.assertIsInstance(track, Track)
        self.assertEquals(
            track.uri,
            'https://api.soundcloud.com/tracks/'
            '38720262/stream?client_id=93e33e327fd8a9b77becd179652272e2'
        )
