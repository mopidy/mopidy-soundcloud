from __future__ import unicode_literals

import logging

from mopidy import backend
from mopidy.models import Playlist

logger = logging.getLogger(__name__)


class SoundCloudPlaylistsProvider(backend.PlaylistsProvider):

    def __init__(self, *args, **kwargs):
        super(SoundCloudPlaylistsProvider, self).__init__(*args, **kwargs)
        self.config = self.backend.config
        self._playlists = []
        self.refresh()

    def create(self, name):
        pass  # TODO

    def delete(self, uri):
        pass  # TODO

    def lookup(self, uri):
        for playlist in self._playlists:
            if playlist.uri == uri:
                # Special case with sets, which already contain all data
                if 'soundcloud:set-' in uri:
                    return playlist

    def refresh(self):

        for (name, uri, tracks) in self.backend.sc_api.get_sets():
            scset = Playlist(
                uri='soundcloud:set-%s' % uri,
                name=name,
                tracks=tracks
            )
            self._playlists.append(scset)

        logger.info('Loaded %d SoundCloud playlist(s)', len(self._playlists))
        backend.BackendListener.send('playlists_loaded')

    def save(self, playlist):
        pass  # TODO
