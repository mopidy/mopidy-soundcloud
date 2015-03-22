from __future__ import unicode_literals

import unittest

import mock

from mopidy.models import Track

import vcr

from mopidy_soundcloud import SoundCloudExtension
from mopidy_soundcloud.soundcloud import SoundCloudClient, readable_url


class ApiTest(unittest.TestCase):
    @vcr.use_cassette('tests/fixtures/sc-login.yaml')
    def setUp(self):
        config = SoundCloudExtension().get_config_schema()
        config['auth_token'] = '1-35204-61921957-55796ebef403996'
        config['explore_songs'] = 10
        # using this user http://maildrop.cc/inbox/mopidytestuser
        self.api = SoundCloudClient(config)

    def test_resolves_string(self):
        _id = self.api.parse_track_uri('soundcloud:song.38720262')
        self.assertEquals(_id, '38720262')

    @vcr.use_cassette('tests/fixtures/sc-login-error.yaml')
    def test_responds_with_error(self):
        with mock.patch('mopidy_soundcloud.soundcloud.logger.error') as d:
            config = SoundCloudExtension().get_config_schema()
            config['auth_token'] = '1-fake-token'
            SoundCloudClient(config)
            d.assert_called_once_with('Invalid "auth_token" used for '
                                      'SoundCloud authentication!')

    @vcr.use_cassette('tests/fixtures/sc-resolve-track.yaml')
    def test_resolves_object(self):
        trackc = {}
        trackc[b'uri'] = 'soundcloud:song.38720262'
        track = Track(**trackc)

        id = self.api.parse_track_uri(track)
        self.assertEquals(id, '38720262')

    @vcr.use_cassette('tests/fixtures/sc-resolve-track-none.yaml')
    def test_resolves_emptyTrack(self):
        track = self.api.get_track('s38720262')
        self.assertIsInstance(track, Track)
        self.assertEquals(track.uri, None)

    @vcr.use_cassette('tests/fixtures/sc-resolve-track.yaml')
    def test_resolves_Track(self):
        track = self.api.get_track('38720262')
        self.assertIsInstance(track, Track)
        self.assertEquals(
            track.uri,
            'soundcloud:song/Burial Four Tet - Nova.38720262'
        )

    @vcr.use_cassette('tests/fixtures/sc-resolve-http.yaml')
    def test_resolves_http_url(self):
        track = self.api.resolve_url(
            'https://soundcloud.com/bbc-radio-4/m-w-cloud'
        )[0]
        self.assertIsInstance(track, Track)
        self.assertEquals(
            track.uri,
            'soundcloud:song/That Mitchell and Webb Sound The Cloud.122889665'
        )

    @vcr.use_cassette('tests/fixtures/sc-liked.yaml')
    def test_get_user_liked(self):
        tracks = self.api.get_user_liked()
        self.assertIsInstance(tracks, list)

    @vcr.use_cassette('tests/fixtures/sc-stream.yaml')
    def test_get_user_stream(self):
        tracks = self.api.get_user_stream()
        self.assertIsInstance(tracks, list)

    @vcr.use_cassette('tests/fixtures/sc-explore.yaml')
    def test_get_explore(self):
        tracks = self.api.get_explore()
        self.assertIsInstance(tracks, list)
        self.assertEquals(tracks[0], 'Popular+Music')

    @vcr.use_cassette('tests/fixtures/sc-popular.yaml')
    def test_get_explore_popular_music(self):
        tracks = self.api.get_explore('1')
        self.assertIsInstance(tracks, list)
        self.assertIsInstance(tracks[0], Track)

    @vcr.use_cassette('tests/fixtures/sc-following.yaml')
    def test_get_followings(self):
        tracks = self.api.get_followings()
        self.assertIsInstance(tracks, list)

    @vcr.use_cassette('tests/fixtures/sc-sets.yaml')
    def test_get_sets(self):
        tracks = self.api.get_sets()
        self.assertIsInstance(tracks, list)

    @vcr.use_cassette('tests/fixtures/sc-groups.yaml')
    def test_get_groups(self):
        tracks = self.api.get_groups()
        self.assertIsInstance(tracks, list)

    @vcr.use_cassette('tests/fixtures/sc-tracks.yaml')
    def test_get_group_tracks(self):
        tracks = self.api.get_groups(136)
        self.assertIsInstance(tracks[0], Track)

    def test_readeble_url(self):
        self.assertEquals('Barsuk Records',
                          readable_url('"@"Barsuk      Records'))
        self.assertEquals('_Barsuk Records',
                          readable_url('_Barsuk \'Records\''))

    @vcr.use_cassette('tests/fixtures/sc-resolve-track-id.yaml')
    def test_resolves_stream_Track(self):
        track = self.api.get_track('38720262', True)
        self.assertIsInstance(track, Track)
        self.assertEquals(
            track.uri,
            'https://api.soundcloud.com/tracks/'
            '38720262/stream?client_id=93e33e327fd8a9b77becd179652272e2'
        )
