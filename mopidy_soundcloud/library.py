import collections
import logging
import re
import urllib.parse

from mopidy import backend, models
from mopidy.models import SearchResult, Track

logger = logging.getLogger(__name__)


def generate_uri(path):
    return f"soundcloud:directory:{urllib.parse.quote('/'.join(path))}"


def new_folder(name, path):
    return models.Ref.directory(uri=generate_uri(path), name=name)


def simplify_search_query(query):

    if isinstance(query, dict):
        r = []
        for v in query.values():
            if isinstance(v, list):
                r.extend(v)
            else:
                r.append(v)
        return " ".join(r)
    if isinstance(query, list):
        return " ".join(query)
    else:
        return query


class SoundCloudLibraryProvider(backend.LibraryProvider):
    root_directory = models.Ref.directory(
        uri="soundcloud:directory", name="SoundCloud"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vfs = {"soundcloud:directory": {}}
        self.add_to_vfs(new_folder("Following", ["following"]))
        self.add_to_vfs(new_folder("Liked", ["liked"]))
        self.add_to_vfs(new_folder("Sets", ["sets"]))
        self.add_to_vfs(new_folder("Stream", ["stream"]))

    def add_to_vfs(self, _model):
        self.vfs["soundcloud:directory"][_model.uri] = _model

    def list_sets(self):
        sets_vfs = collections.OrderedDict()
        for (name, set_id, _tracks) in self.backend.remote.get_sets():
            sets_list = new_folder(name, ["sets", set_id])
            logger.debug(f"Adding set {sets_list.name} to VFS")
            sets_vfs[set_id] = sets_list
        return list(sets_vfs.values())

    def list_liked(self):
        vfs_list = collections.OrderedDict()
        for track in self.backend.remote.get_likes():
            logger.debug(f"Adding liked track {track.name} to VFS")
            vfs_list[track.name] = models.Ref.track(
                uri=track.uri, name=track.name
            )
        return list(vfs_list.values())

    def list_user_follows(self):
        sets_vfs = collections.OrderedDict()
        for (name, user_id) in self.backend.remote.get_followings():
            sets_list = new_folder(name, ["following", user_id])
            logger.debug(f"Adding set {sets_list.name} to VFS")
            sets_vfs[user_id] = sets_list
        return list(sets_vfs.values())

    def tracklist_to_vfs(self, track_list):
        vfs_list = collections.OrderedDict()
        for temp_track in track_list:
            if not isinstance(temp_track, Track):
                temp_track = self.backend.remote.parse_track(temp_track)
            if hasattr(temp_track, "uri"):
                vfs_list[temp_track.name] = models.Ref.track(
                    uri=temp_track.uri, name=temp_track.name
                )
        return list(vfs_list.values())

    def browse(self, uri):
        if not self.vfs.get(uri):
            (req_type, res_id) = re.match(r".*:(\w*)(?:/(\d*))?", uri).groups()
            # Sets
            if "sets" == req_type:
                if res_id:
                    return self.tracklist_to_vfs(
                        self.backend.remote.get_set(res_id)
                    )
                else:
                    return self.list_sets()
            # Following
            if "following" == req_type:
                if res_id:
                    return self.tracklist_to_vfs(
                        self.backend.remote.get_tracks(res_id)
                    )
                else:
                    return self.list_user_follows()
            # Liked
            if "liked" == req_type:
                return self.list_liked()
            # User stream
            if "stream" == req_type:
                return self.tracklist_to_vfs(
                    self.backend.remote.get_user_stream()
                )

        # root directory
        return list(self.vfs.get(uri, {}).values())

    def search(self, query=None, uris=None, exact=False):
        # TODO Support exact search

        if not query:
            return

        if "uri" in query:
            search_query = "".join(query["uri"])
            url = urllib.parse.urlparse(search_query)
            if "soundcloud.com" in url.netloc:
                logger.info(f"Resolving SoundCloud for: {search_query}")
                return SearchResult(
                    uri="soundcloud:search",
                    tracks=self.backend.remote.resolve_url(search_query),
                )
        else:
            search_query = simplify_search_query(query)
            logger.info(f"Searching SoundCloud for: {search_query}")
            return SearchResult(
                uri="soundcloud:search",
                tracks=self.backend.remote.search(search_query),
            )

    def lookup(self, uri):
        if "sc:" in uri:
            uri = uri.replace("sc:", "")
            return self.backend.remote.resolve_url(uri)

        try:
            track_id = self.backend.remote.parse_track_uri(uri)
            track = self.backend.remote.get_track(track_id)
            if track is None:
                logger.info(
                    f"Failed to lookup {uri}: SoundCloud track not found"
                )
                return []
            return [track]
        except Exception as error:
            logger.error(f"Failed to lookup {uri}: {error}")
            return []
