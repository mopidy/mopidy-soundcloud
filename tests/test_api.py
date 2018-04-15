from __future__ import unicode_literals

import os.path
import unittest

import mock

from mopidy.models import Track

import vcr

from mopidy_soundcloud import SoundCloudExtension
from mopidy_soundcloud.soundcloud import SoundCloudClient, readable_url

local_path = os.path.abspath(os.path.dirname(__file__))
my_vcr = vcr.VCR(serializer='yaml',
                 cassette_library_dir=local_path + '/fixtures',
                 record_mode='once',
                 match_on=['uri', 'method'],
                 )


class ApiTest(unittest.TestCase):
    @my_vcr.use_cassette('sc-login.yaml')
    def setUp(self):
        config = SoundCloudExtension().get_config_schema()
        config['auth_token'] = '1-35204-61921957-55796ebef403996'
        config['explore_songs'] = 10
        # using this user http://maildrop.cc/inbox/mopidytestuser
        self.api = SoundCloudClient({'soundcloud': config, 'proxy': {}})

    def test_resolves_string(self):
        _id = self.api.parse_track_uri('soundcloud:song.38720262')
        self.assertEquals(_id, '38720262')

    @my_vcr.use_cassette('sc-login-error.yaml')
    def test_responds_with_error(self):
        with mock.patch('mopidy_soundcloud.soundcloud.logger.error') as d:
            config = SoundCloudExtension().get_config_schema()
            config['auth_token'] = '1-fake-token'
            SoundCloudClient({'soundcloud': config, 'proxy': {}}).user
            d.assert_called_once_with('Invalid "auth_token" used for '
                                      'SoundCloud authentication!')

    @my_vcr.use_cassette('sc-login.yaml')
    def test_returns_username(self):
        user = self.api.user.get('username')
        self.assertEquals(user, 'ticosax')

    @my_vcr.use_cassette('sc-resolve-track.yaml')
    def test_resolves_object(self):
        trackc = {}
        trackc[b'uri'] = 'soundcloud:song.38720262'
        track = Track(**trackc)

        id = self.api.parse_track_uri(track)
        self.assertEquals(id, '38720262')

    @my_vcr.use_cassette('sc-resolve-track-none.yaml')
    def test_resolves_unknown_track_to_none(self):
        track = self.api.get_track('s38720262')
        self.assertIsNone(track)

    @my_vcr.use_cassette('sc-resolve-track.yaml')
    def test_resolves_Track(self):
        track = self.api.get_track('13158665')
        self.assertIsInstance(track, Track)
        self.assertEquals(
            track.uri,
            'soundcloud:song/Munching at Tiannas house.13158665'
        )

    @my_vcr.use_cassette('sc-resolve-http.yaml')
    def test_resolves_http_url(self):
        track = self.api.resolve_url(
            'https://soundcloud.com/bbc-radio-4/m-w-cloud'
        )[0]
        self.assertIsInstance(track, Track)
        self.assertEquals(
            track.uri,
            'soundcloud:song/That Mitchell and Webb Sound The Cloud.122889665'
        )

    @my_vcr.use_cassette('sc-liked.yaml')
    def test_get_user_liked(self):
        tracks = self.api.get_user_liked()
        self.assertIsInstance(tracks, list)

    @my_vcr.use_cassette('sc-stream.yaml')
    def test_get_user_stream(self):
        tracks = self.api.get_user_stream()
        self.assertIsInstance(tracks, list)

    @my_vcr.use_cassette('sc-following.yaml')
    def test_get_followings(self):
        tracks = self.api.get_followings()
        self.assertIsInstance(tracks, list)

    @my_vcr.use_cassette('sc-sets.yaml')
    def test_get_sets(self):
        tracks = self.api.get_sets()
        self.assertIsInstance(tracks, list)

    def test_readeble_url(self):
        self.assertEquals('Barsuk Records',
                          readable_url('"@"Barsuk      Records'))
        self.assertEquals('_Barsuk Records',
                          readable_url('_Barsuk \'Records\''))

    @my_vcr.use_cassette('sc-resolve-track-id.yaml')
    def test_resolves_stream_track(self):
        track = self.api.get_track('13158665', True)
        self.assertIsInstance(track, Track)
        self.assertEquals(
            track.uri,
            'https://cf-media.sndcdn.com/fxguEjG4ax6B.128.mp3?Policy=eyJTdGF0ZW'
            '1lbnQiOlt7IlJlc291cmNlIjoiKjovL2NmLW1lZGlhLnNuZGNkbi5jb20vZnhndUVq'
            'RzRheDZCLjEyOC5tcDMiLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUz'
            'pFcG9jaFRpbWUiOjE0Nzc2MDA1NTd9fX1dfQ__&Signature=u9bxAkZOtTTF1VqTm'
            'LGmw3ENrqbiSTFK-sMvZL-ZsQK85DOepHh5MfPA4MNooszUy~PZqiVyBn4YnElhWyb'
            '~4B7kS6y0VZ6t-qF78CfTMOimemafpqfWJ8nYXczhM9pUpAwiS--lkNjGks4Qxi-FZ'
            'JDBPG99gAIU0eVW78CADcpuOKLugGpzHl6gRPN2Z4zZ9dVujZ5MlG2OWnPuNiBcE~w'
            'UFwcOxt9N6ePTff-wMFQR2PGpEK6wc6bWuB4WFNBkE0bmEke4cOQjWHa5FwYEidZN5'
            'rvv5lVT1r07zzifnADEipwMaZ2-QYdqzOYaM4jymFDhl7DklaU24PY5C5mH0A__&Ke'
            'y-Pair-Id=APKAJAGZ7VMH2PFPW6UQ'
        )
