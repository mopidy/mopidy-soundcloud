import itertools
import logging
import operator
import urllib.parse

from mopidy import models
from mopidy_soundcloud.soundcloud import SoundCloudClient

# NOTE: current file adapted from https://github.com/mopidy/mopidy-spotify
#   - /mopidy-spotify/images.py

logger = logging.getLogger(__name__)


class SoundCloudImageProvider:
    _API_MAX_IDS_PER_REQUEST = 50

    _cache = {}  # (type, id) -> [Image(), ...]

    # For reference
    _ARTWORK_MAP = {
        "mini": 16,
        "tiny": 20,
        "small": 32,
        "badge": 47,
        "t67x67": 67,
        "large": 100,
        "t300x300": 300,
        "crop": 400,
        "t500x500": 500,
        "original": 0,
    }

    def __init__(self, web_client: SoundCloudClient):
        self.web_client = web_client

    def get_images(self, uris):
        result = {}
        uri_type_getter = operator.itemgetter("type")
        uris = sorted((self._parse_uri(u) for u in uris), key=uri_type_getter)
        for uri_type, group in itertools.groupby(uris, uri_type_getter):
            batch = []
            for uri in group:
                if uri["key"] in self._cache:
                    result[uri["uri"]] = self._cache[uri["key"]]
                elif uri_type == "playlist":
                    result.update(self._process_set(uri))
                else:
                    batch.append(uri)
                    if len(batch) >= self._API_MAX_IDS_PER_REQUEST:
                        result.update(self._process_uris(batch))
                        batch = []
            result.update(self._process_uris(batch))
        return result

    def _parse_uri(self, uri):
        parsed_uri = urllib.parse.urlparse(uri)
        uri_type, uri_id = None, None

        if parsed_uri.scheme == "soundcloud":
            uri_type, uri_id = parsed_uri.path.split("/")[:2]
        elif parsed_uri.scheme in ("http", "https"):
            if "soundcloud.com" in parsed_uri.netloc:
                uri_type, uri_id = parsed_uri.path.split("/")[1:3]

        supported_types = ("song", "album", "artist", "playlist")
        if uri_type and uri_type in supported_types and uri_id:
            return {
                "uri": uri,
                "type": uri_type,
                "id": self.web_client.parse_track_uri(uri_id),
                "key": (uri_type, uri_id),
            }

        raise ValueError(f"Could not parse {repr(uri)} as a SoundCloud URI")

    def _process_set(self, uri):
        tracks = self.web_client.get_set(uri["id"])
        set_images = tuple()
        for track in tracks:
            set_images += (*self._process_track(track),)

        self._cache[uri["key"]] = set_images

        return {uri["uri"]: set_images}

    def _process_uris(self, uris):
        result = {}
        for uri in uris:
            if uri["key"] not in self._cache:
                track = self.web_client.get_track(uri["id"])
                self._cache[uri["key"]] = self._process_track(track)

            result.update({uri["uri"]: self._cache[uri["key"]]})
        return result

    @staticmethod
    def _process_track(track):
        images = []
        if track:
            image_sources = track["artwork_url"], track["user"]["avatar_url"]
            for image_url in image_sources:
                if image_url is not None:
                    image_url = image_url.replace("large", "t500x500")
                    image = models.Image(uri=image_url, height=500, width=500)
                    images.append(image)
        return tuple(images)
