from __future__ import unicode_literals
import collections

import logging
import re
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
            sets_list = self.new_folder(name, ['sets', set_id])
            logger.debug('Adding set %s to vfs' % sets_list.name)
            sets_vfs[set_id] = sets_list
        return sets_vfs.values()

    def list_user_follows(self):
        sets_vfs = collections.OrderedDict()
        for (name, user_id) in self.backend.remote.get_followings():
            sets_list = self.new_folder(name, ['following', user_id])
            logger.debug('Adding set %s to vfs' % sets_list.name)
            sets_vfs[user_id] = sets_list
        return sets_vfs.values()

    def tracklist_to_vfs(self, track_list):
        vfs_list = collections.OrderedDict()
        for temp_track in track_list:
            if not isinstance(temp_track, Track):
                temp_track = self.backend.remote.parse_track(temp_track)
            if hasattr(temp_track, 'uri'):
                vfs_list[temp_track.name] = models.Ref.track(
                    uri=temp_track.uri,
                    name=temp_track.name
                )
        return vfs_list.values()

    def browse(self, uri):
        if not self.vfs.get(uri):
            (req_type, res_id) = re.match(r'.*:(\w*)(?:/(\d*))?', uri).groups()
            # Sets
            if 'sets' == req_type:
                if res_id:
                    return self.tracklist_to_vfs(
                        self.backend.remote.get_sets(res_id)
                    )
                else:
                    return self.list_sets()
            # Following
            if 'following' == req_type:
                if res_id:
                    return self.tracklist_to_vfs(
                        self.backend.remote.get_followings(res_id)
                    )
                else:
                    return self.list_user_follows()
            # Liked
            if 'liked' == req_type:
                return self.tracklist_to_vfs(
                    self.backend.remote.get_user_liked()
                )
            # User stream
            if 'stream' == req_type:
                return self.tracklist_to_vfs(
                    self.backend.remote.get_user_stream(res_id)
                )

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
