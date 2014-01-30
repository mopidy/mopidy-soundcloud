from __future__ import unicode_literals
import collections

import logging
import urllib

from mopidy import backend, models
from mopidy.models import SearchResult, Track


logger = logging.getLogger(__name__)


class SoundCloudLibraryProvider(backend.LibraryProvider):

    def __init__(self, *args, **kwargs):
        super(SoundCloudLibraryProvider, self).__init__(*args, **kwargs)
        self.vfs = {'soundcloud:directory': collections.OrderedDict()}
        self.add_to_vfs(self.new_folder('Explore', ['explore']))
        self.add_to_vfs(self.new_folder('Following', ['following']))
        self.add_to_vfs(self.new_folder('Liked', ['liked']))
        self.add_to_vfs(self.new_folder('Sets', ['sets']))
        self.add_to_vfs(self.new_folder('Stream', ['stream']))

    root_directory = models.Ref.directory(
        uri=b'soundcloud:directory',
        name='SoundCloud'
    )

    def new_folder(self, name, path):
        return models.Ref.directory(
            uri=self.generate_uri(path),
            name=name
        )

    def add_to_vfs(self, _model):
        self.vfs['soundcloud:directory'][_model.uri] = _model

    def list_sets(self):
        sets_vfs = collections.OrderedDict()
        for (name, set_id, tracks) in self.backend.remote.get_sets():
            lset = self.new_folder(name, ['sets', set_id])
            logger.debug('Adding set %s to vfs' % lset.name)
            sets_vfs[set_id] = lset
        return sets_vfs.values()

    def show_set(self, urn):
        set_vfs = collections.OrderedDict()
        set_id = urn.split('/')[-1]
        for track in self.backend.remote.get_sets(set_id):
            ttrack = self.backend.remote.parse_track(track)
            if isinstance(ttrack, Track):
                set_vfs[track.get('id')] = models.Ref.track(
                    uri=ttrack.uri,
                    name=ttrack.name
                )
        return set_vfs.values()

    def browse(self, uri):
        if not self.vfs.get(uri):
            uri_type = uri.split(':')[-1]
            logger.info('uri_type %s' % uri_type)

            # Sets
            if 'sets/' in uri_type:
                return self.show_set(uri)
            if uri_type == 'sets':
                return self.list_sets()

        # root directory
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
                    tracks=self.backend.remote.search(query['artist']) or [])
            elif field == "any":
                return SearchResult(
                    uri='soundcloud:search',
                    tracks=self.backend.remote.search(val[0]) or [])
            else:
                return []

    def lookup(self, uri):
        try:
            track_id = self.backend.remote.parse_track_uri(uri)
            return [self.backend.remote.get_track(track_id)]
        except Exception as error:
            logger.error(u'Failed to lookup %s: %s', uri, error)
            return []

    def generate_uri(self, path):
        return b'soundcloud:directory:%s' % urllib.quote('/'.join(path))
