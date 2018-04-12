from __future__ import unicode_literals

import logging

from mopidy import backend

import pykka

from .library import SoundCloudLibraryProvider
from .soundcloud import SoundCloudClient


logger = logging.getLogger(__name__)


class SoundCloudBackend(pykka.ThreadingActor, backend.Backend):

    def __init__(self, config, audio):
        super(SoundCloudBackend, self).__init__()
        self.config = config
        self.remote = SoundCloudClient(config)
        self.library = SoundCloudLibraryProvider(backend=self)
        self.playback = SoundCloudPlaybackProvider(audio=audio, backend=self)

        self.uri_schemes = ['soundcloud', 'sc']

    def on_start(self):
        username = self.remote.user.get('username')
        if username is not None:
            logger.info('Logged in to SoundCloud as "%s"', username)


class SoundCloudPlaybackProvider(backend.PlaybackProvider):

    def translate_uri(self, uri):
        track_id = self.backend.remote.parse_track_uri(uri)
        track = self.backend.remote.get_track(track_id, True)
        if track is None:
            return None
        return track.uri
