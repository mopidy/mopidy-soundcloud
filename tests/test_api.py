from __future__ import unicode_literals

import os.path
import unittest

import mock

from mopidy.models import Track

import vcr

import mopidy_soundcloud
from mopidy_soundcloud import SoundCloudExtension
from mopidy_soundcloud.soundcloud import SoundCloudClient, readable_url

local_path = os.path.abspath(os.path.dirname(__file__))
my_vcr = vcr.VCR(serializer='yaml',
                 cassette_library_dir=local_path + '/fixtures',
                 record_mode='once',
                 match_on=['uri', 'method'],
                 decode_compressed_response=False,
                 filter_headers=['Authorization']
                 )


class ApiTest(unittest.TestCase):
    @my_vcr.use_cassette('sc-login.yaml')
    def setUp(self):
        config = SoundCloudExtension().get_config_schema()
        config['auth_token'] = '1-35204-61921957-55796ebef403996'
        config['explore_songs'] = 10
        self.api = SoundCloudClient({'soundcloud': config, 'proxy': {}})

    def test_sets_user_agent(self):
        agent = 'Mopidy-SoundCloud/%s Mopidy/' % mopidy_soundcloud.__version__
        self.assertTrue(agent in self.api.http_client.headers['user-agent'])

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
        self.assertEquals(user, 'Nick Steel 3')

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

    @my_vcr.use_cassette('sc-resolve-set.yaml')
    def test_resolves_set_url(self):
        expected_tracks = ['01 Dash And Blast',
                           '02 We Flood Empty Lakes',
                           '03 A Song For Starlit Beaches',
                           '04 Illuminate My Heart, My Darling']
        tracks = self.api.resolve_url(
            'https://soundcloud.com/yndihalda/sets/dash-and-blast'
        )
        self.assertEquals(len(tracks), 4)
        for i, t in enumerate(expected_tracks):
            self.assertIsInstance(tracks[i], Track)
            self.assertEquals(tracks[i].name, expected_tracks[i])
            self.assertTrue(tracks[i].length > 500)
            self.assertEquals(len(tracks[i].artists), 1)
            self.assertEquals(list(tracks[i].artists)[0].name, 'yndi halda')

    @my_vcr.use_cassette('sc-liked.yaml')
    def test_get_user_likes(self):
        tracks = self.api.get_likes()
        self.assertEquals(len(tracks), 3)
        self.assertIsInstance(tracks[0], Track)
        self.assertEquals(tracks[1].name, 'Pelican - Deny The Absolute')

    @my_vcr.use_cassette('sc-stream.yaml')
    def test_get_user_stream(self):
        tracks = self.api.get_user_stream()
        self.assertEquals(len(tracks), 10)
        self.assertIsInstance(tracks[0], Track)
        self.assertEquals(tracks[2].name, 'JW Ep 20- Jeremiah Watkins')

    @my_vcr.use_cassette('sc-following.yaml')
    def test_get_followings(self):
        users = self.api.get_followings()
        self.assertEquals(len(users), 10)
        self.assertEquals(users[0], (u'Young Legionnaire', '992503'))
        self.assertEquals(users[1], (u'Tall Ships', '1710483'))
        self.assertEquals(users[8], (u'Pelican Song', '27945548'))
        self.assertEquals(users[9], (u'sleepmakeswaves', '1739693'))

    @my_vcr.use_cassette('sc-user-tracks.yaml')
    def test_get_user_tracks(self):
        expected_tracks = ['The Wait',
                           'The Cliff (Palms Remix)',
                           'The Cliff (Justin Broadrick Remix)',
                           'The Cliff (Vocal Version)',
                           'Pelican - The Creeper',
                           'Pelican - Lathe Biosas',
                           'Pelican - Ephemeral',
                           'Pelican - Deny the Absolute',
                           'Pelican - Immutable Dusk',
                           'Pelican - Strung Up From The Sky']

        tracks = self.api.get_tracks(27945548)
        for i, t in enumerate(expected_tracks):
            self.assertIsInstance(tracks[i], Track)
            self.assertEquals(tracks[i].name, expected_tracks[i])
            self.assertTrue(tracks[i].length > 500)
            self.assertEquals(len(tracks[i].artists), 1)

    @my_vcr.use_cassette('sc-set.yaml')
    def test_get_set(self):
        tracks = self.api.get_set('10961826')
        self.assertEquals(len(tracks), 1)
        self.assertIsInstance(tracks[0], dict)

    @my_vcr.use_cassette('sc-set-invalid.yaml')
    def test_get_invalid_set(self):
        tracks = self.api.get_set('blahblahrubbosh')
        self.assertEquals(tracks, [])

    @my_vcr.use_cassette('sc-sets.yaml')
    def test_get_sets(self):
        sets = self.api.get_sets()
        self.assertEquals(len(sets), 2)
        name, set_id, tracks = sets[1]
        self.assertEquals(name, 'Pelican')
        self.assertEquals(set_id, '10961826')
        self.assertEquals(len(tracks), 1)

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
            'https://cf-media.sndcdn.com/fxguEjG4ax6B.128.mp3?Policy=eyJTdGF0Z'
            'W1lbnQiOlt7IlJlc291cmNlIjoiKjovL2NmLW1lZGlhLnNuZGNkbi5jb20vZnhndU'
            'VqRzRheDZCLjEyOC5tcDMiLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkF'
            'XUzpFcG9jaFRpbWUiOjE0Nzc2MDA1NTd9fX1dfQ__&Signature=u9bxAkZOtTTF1'
            'VqTmLGmw3ENrqbiSTFK-sMvZL-ZsQK85DOepHh5MfPA4MNooszUy~PZqiVyBn4YnE'
            'lhWyb~4B7kS6y0VZ6t-qF78CfTMOimemafpqfWJ8nYXczhM9pUpAwiS--lkNjGks4'
            'Qxi-FZJDBPG99gAIU0eVW78CADcpuOKLugGpzHl6gRPN2Z4zZ9dVujZ5MlG2OWnPu'
            'NiBcE~wUFwcOxt9N6ePTff-wMFQR2PGpEK6wc6bWuB4WFNBkE0bmEke4cOQjWHa5F'
            'wYEidZN5rvv5lVT1r07zzifnADEipwMaZ2-QYdqzOYaM4jymFDhl7DklaU24PY5C5'
            'mH0A__&Key-Pair-Id=APKAJAGZ7VMH2PFPW6UQ'
        )

    @my_vcr.use_cassette('sc-search.yaml')
    def test_search(self):
        tracks = self.api.search('the great descent')
        self.assertEquals(len(tracks), 10)
        self.assertIsInstance(tracks[0], Track)
        self.assertEquals(tracks[0].name, 'Turn Around (Mix1)')
