from __future__ import unicode_literals
import collections

import logging
import urllib

from mopidy import backend, models
from mopidy.models import SearchResult


logger = logging.getLogger(__name__)


class SoundCloudLibraryProvider(backend.LibraryProvider):
    def __init__(self, *args, **kwargs):
        super(SoundCloudLibraryProvider, self).__init__(*args, **kwargs)
        self.vfs = {'soundcloud:directory': collections.OrderedDict()}
        self.add_to_vfs(self.new_folder('Explore', ['explore']))
        self.add_to_vfs(self.new_folder('Stream', ['stream']))
        self.add_to_vfs(self.new_folder('Following', ['following']))

    root_directory = models.Ref.directory(
        uri=b'soundcloud:directory',
        name='SoundCloud'
    )

    def new_folder(self, name, path):
        return models.Ref.directory(
            uri=b'soundcloud:directory:' + urllib.quote('/'.join(path)),
            name=name
        )

    def add_to_vfs(self, _model):
        self.vfs['soundcloud:directory'][_model.uri] = _model

    def browse(self, uri):
        return self.vfs.get(uri, {}).values()

    def find_exact(self, **query):
        return self.search(**query)

    def search(self, **query):
        if not query:
            return

        for (field, val) in query.iteritems():

            # TODO: Devise method for searching SoundCloud via artists
            if field == "album" and query['album'] == "SoundCloud":
                return SearchResult(
                    uri='soundcloud:search',
                    tracks=self.backend.sc_api.search(query['artist']) or [])
            elif field == "any":
                return SearchResult(
                    uri='soundcloud:search',
                    tracks=self.backend.sc_api.search(val[0]) or [])
            else:
                return []

    def lookup(self, uri):
        try:
            id = self.backend.sc_api.parse_track_uri(uri)
            return [self.backend.sc_api.get_track(id)]
        except Exception as error:
            logger.error(u'Failed to lookup %s: %s', uri, error)
            return []
