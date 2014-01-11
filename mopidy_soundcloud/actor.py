from __future__ import unicode_literals

import logging
import pykka

from mopidy.backends import base

from .library import SoundCloudLibraryProvider
from .playlists import SoundCloudPlaylistsProvider
from .soundcloud import SoundCloudClient

logger = logging.getLogger(__name__)


class SoundCloudBackend(pykka.ThreadingActor, base.Backend):

    def __init__(self, config, audio):
        super(SoundCloudBackend, self).__init__()
        self.config = config
        self.sc_api = SoundCloudClient(config['soundcloud']['auth_token'])
        self.library = SoundCloudLibraryProvider(backend=self)
        self.playback = SoundCloudPlaybackProvider(audio=audio, backend=self)
        self.playlists = SoundCloudPlaylistsProvider(backend=self)

        self.uri_schemes = ['soundcloud']


class SoundCloudPlaybackProvider(base.BasePlaybackProvider):

    def play(self, track):
        id = self.backend.sc_api.parse_track_uri(track)
        track = self.backend.sc_api.get_track(id, True)
        return super(SoundCloudPlaybackProvider, self).play(track)
