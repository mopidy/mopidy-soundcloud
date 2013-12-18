from __future__ import unicode_literals

import unittest
from mopidy.models import Track

from mopidy_soundcloud.soundcloud import SoundCloudClient


class ApiTest(unittest.TestCase):
    # using this user http://maildrop.cc/inbox/mopidytestuser
    api = SoundCloudClient("1-35204-61921957-55796ebef403996")

    def test_resolves_string(self):
        id = self.api.parse_track_uri("soundcloud:song;38720262")
        self.assertEquals(id, "38720262")

    def test_resolves_object(self):

        trackc = {}
        trackc[b'uri'] = 'soundcloud:song;38720262'
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
        self.assertEquals(track.uri, 'soundcloud:song;38720262')

    def test_resolves_stream_Track(self):

        track = self.api.get_track('38720262', True)
        self.assertIsInstance(track, Track)
        self.assertEquals(
            track.uri,
            'https://api.soundcloud.com/tracks/'
            '38720262/stream?client_id=93e33e327fd8a9b77becd179652272e2'
        )
