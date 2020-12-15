import collections
import datetime
import logging
import re
import string
import time
import unicodedata
from contextlib import closing
from multiprocessing.pool import ThreadPool
from urllib.parse import quote_plus

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError

import mopidy_soundcloud
from mopidy import httpclient
from mopidy.models import Album, Artist, Track

logger = logging.getLogger(__name__)


def safe_url(uri):
    return quote_plus(
        unicodedata.normalize("NFKD", uri).encode("ASCII", "ignore")
    )


def readable_url(uri):
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    safe_uri = (
        unicodedata.normalize("NFKD", uri).encode("ascii", "ignore").decode()
    )
    return re.sub(
        r"\s+", " ", "".join(c for c in safe_uri if c in valid_chars)
    ).strip()


def streamble_url(url, client_id):
    return f"{url}?client_id={client_id}"


def get_user_url(user_id):
    if not user_id:
        return "me"
    else:
        return f"users/{user_id}"


def get_requests_session(proxy_config, user_agent, token):
    proxy = httpclient.format_proxy(proxy_config)
    full_user_agent = httpclient.format_user_agent(user_agent)

    session = requests.Session()
    session.proxies.update({"http": proxy, "https": proxy})
    session.headers.update({"user-agent": full_user_agent})
    session.headers.update({"Authorization": f"OAuth {token}"})

    return session


class cache:  # noqa
    # TODO: merge this to util library

    def __init__(self, ctl=8, ttl=3600):
        self.cache = {}
        self.ctl = ctl
        self.ttl = ttl
        self._call_count = 1

    def __call__(self, func):
        def _memoized(*args):
            self.func = func
            now = time.time()
            try:
                value, last_update = self.cache[args]
                age = now - last_update
                if self._call_count >= self.ctl or age > self.ttl:
                    self._call_count = 1
                    raise AttributeError

                self._call_count += 1
                return value

            except (KeyError, AttributeError):
                value = self.func(*args)
                self.cache[args] = (value, now)
                return value

            except TypeError:
                return self.func(*args)

        return _memoized


class ThrottlingHttpAdapter(HTTPAdapter):
    def __init__(self, burst_length, burst_window, wait_window):
        super().__init__()
        self.max_hits = burst_length
        self.hits = 0
        self.rate = burst_length / burst_window
        self.burst_window = datetime.timedelta(seconds=burst_window)
        self.total_window = datetime.timedelta(
            seconds=burst_window + wait_window
        )
        self.timestamp = datetime.datetime.min

    def _is_too_many_requests(self):
        now = datetime.datetime.utcnow()
        if now < self.timestamp + self.total_window:
            elapsed = now - self.timestamp
            self.hits += 1
            if (now < self.timestamp + self.burst_window) and (
                self.hits < self.max_hits
            ):
                return False
            else:
                logger.debug(
                    f"Request throttling after {self.hits} hits in "
                    f"{elapsed.microseconds} us "
                    f"(window until {self.timestamp + self.total_window})"
                )
                return True
        else:
            self.timestamp = now
            self.hits = 0
            return False

    def send(self, request, **kwargs):
        if request.method == "HEAD" and self._is_too_many_requests():
            resp = requests.Response()
            resp.request = request
            resp.url = request.url
            resp.status_code = 429
            resp.reason = (
                "Client throttled to {self.rate:.1f} requests per second"
            )
            return resp
        else:
            return super().send(request, **kwargs)


class SoundCloudClient:
    CLIENT_ID = "93e33e327fd8a9b77becd179652272e2"

    def __init__(self, config):
        super().__init__()
        self.explore_songs = config["soundcloud"].get("explore_songs", 25)
        self.http_client = get_requests_session(
            proxy_config=config["proxy"],
            user_agent=(
                f"{mopidy_soundcloud.Extension.dist_name}/"
                f"{mopidy_soundcloud.__version__}"
            ),
            token=config["soundcloud"]["auth_token"],
        )
        adapter = ThrottlingHttpAdapter(
            burst_length=3, burst_window=1, wait_window=10
        )
        self.http_client.mount("https://api.soundcloud.com/", adapter)

    @property
    @cache()
    def user(self):
        return self._get("me")

    @cache(ttl=10)
    def get_user_stream(self):
        # https://developers.soundcloud.com/docs/api/reference#activities
        tracks = []
        stream = self._get("me/activities", limit=True).get("collection", [])
        for data in stream:
            kind = data.get("origin")
            # multiple types of track with same data
            if kind:
                if kind["kind"] == "track":
                    tracks.append(self.parse_track(kind))
                elif kind["kind"] == "playlist":
                    playlist = kind.get("tracks")
                    if isinstance(playlist, collections.Iterable):
                        tracks.extend(self.parse_results(playlist))

        return self.sanitize_tracks(tracks)

    @cache(ttl=10)
    def get_followings(self, user_id=None):
        user_url = get_user_url(user_id)
        users = []
        playlists = self._get(f"{user_url}/followings", limit=True)
        for playlist in playlists.get("collection", []):
            user_name = playlist.get("username")
            user_id = str(playlist.get("id"))
            logger.debug(f"Fetched user {user_name} with ID {user_id}")
            users.append((user_name, user_id))
        return users

    @cache()
    def get_set(self, set_id):
        # https://developers.soundcloud.com/docs/api/reference#playlists
        playlist = self._get(f"playlists/{set_id}")
        return playlist.get("tracks", [])

    @cache(ttl=10)
    def get_sets(self, user_id=None):
        user_url = get_user_url(user_id)
        playable_sets = []
        for playlist in self._get(f"{user_url}/playlists", limit=True):
            name = playlist.get("title")
            set_id = str(playlist.get("id"))
            tracks = playlist.get("tracks", [])
            logger.debug(
                f"Fetched set {name} with ID {set_id} ({len(tracks)} tracks)"
            )
            playable_sets.append((name, set_id, tracks))
        return playable_sets

    @cache(ttl=10)
    def get_likes(self, user_id=None):
        # https://developers.soundcloud.com/docs/api/reference#GET--users--id--favorites
        user_url = get_user_url(user_id)
        likes = self._get(f"{user_url}/favorites", limit=True)
        return self.parse_results(likes)

    @cache(ttl=10)
    def get_tracks(self, user_id=None):
        user_url = get_user_url(user_id)
        tracks = self._get(f"{user_url}/tracks", limit=True)
        return self.parse_results(tracks)

    # Public
    @cache()
    def get_track(self, track_id, streamable=False):
        logger.debug("Getting info for track with ID {track_id}")
        try:
            return self.parse_track(self._get(f"tracks/{track_id}"), streamable)
        except Exception:
            return None

    def parse_track_uri(self, track):
        logger.debug(f"Parsing track {track}")
        if hasattr(track, "uri"):
            track = track.uri
        return track.split(".")[-1]

    def search(self, query):
        # https://developers.soundcloud.com/docs/api/reference#tracks
        query = quote_plus(query.encode("utf-8"))
        search_results = self._get(f"tracks?q={query}", limit=True)
        tracks = []
        for track in search_results:
            tracks.append(self.parse_track(track, False))
        return self.sanitize_tracks(tracks)

    def parse_results(self, res):
        tracks = []
        logger.debug(f"Parsing {len(res)} result item(s)...")
        for item in res:
            if item["kind"] == "track":
                tracks.append(self.parse_track(item))
            elif item["kind"] == "playlist":
                playlist_tracks = item.get("tracks", [])
                logger.debug(
                    f"Parsing {len(playlist_tracks)} playlist track(s)..."
                )
                for track in playlist_tracks:
                    tracks.append(self.parse_track(track))
            else:
                logger.warning(f"Unknown item type {item['kind']!r}")
        return self.sanitize_tracks(tracks)

    def resolve_url(self, uri):
        return self.parse_results([self._get(f"resolve?url={uri}")])

    def _get(self, url, limit=None):
        url = f"https://api.soundcloud.com/{url}"
        params = [("client_id", self.CLIENT_ID)]
        if limit:
            params.insert(0, ("limit", self.explore_songs))
        try:
            with closing(self.http_client.get(url, params=params)) as res:
                logger.debug(f"Requested {res.url}")
                res.raise_for_status()
                return res.json()
        except Exception as e:
            if isinstance(e, HTTPError) and e.response.status_code == 401:
                logger.error(
                    'Invalid "auth_token" used for SoundCloud '
                    "authentication!"
                )
            else:
                logger.error(f"SoundCloud API request failed: {e}")
        return {}

    def sanitize_tracks(self, tracks):
        return [t for t in tracks if t]

    @cache()
    def parse_track(self, data, remote_url=False):
        if not data:
            return None
        if not data.get("streamable"):
            logger.info(
                f"{data.get('title')!r} can't be streamed from SoundCloud"
            )
            return None
        if not data.get("kind") == "track":
            logger.debug(f"{data.get('title')} is not track")
            return None

        track_kwargs = {}
        artist_kwargs = {}
        album_kwargs = {}

        if "title" in data:
            label_name = data.get("label_name")
            if not label_name:
                label_name = data.get("user", {}).get(
                    "username", "Unknown label"
                )

            track_kwargs["name"] = data["title"]
            artist_kwargs["name"] = label_name
            album_kwargs["name"] = "SoundCloud"

        if "date" in data:
            track_kwargs["date"] = data["date"]

        if remote_url:
            track_kwargs["uri"] = self.get_streamble_url(data["stream_url"])
            if track_kwargs["uri"] is None:
                logger.info(
                    f"{data.get('title')} can't be streamed from SoundCloud"
                )
                return None
        else:
            track_kwargs[
                "uri"
            ] = f"soundcloud:song/{readable_url(data.get('title'))}.{data.get('id')}"

        track_kwargs["length"] = int(data.get("duration", 0))
        track_kwargs["comment"] = data.get("permalink_url", "")

        if artist_kwargs:
            track_kwargs["artists"] = [Artist(**artist_kwargs)]

        if album_kwargs:
            track_kwargs["album"] = Album(**album_kwargs)

        return Track(**track_kwargs)

    @cache()
    def get_streamble_url(self, url):
        req = self.http_client.head(streamble_url(url, self.CLIENT_ID))
        if req.status_code == 302:
            return req.headers.get("Location", None)
        elif req.status_code == 429:
            reason = "" if req.reason == "Unknown" else f" ({req.reason})"
            logger.warning(f"SoundCloud daily rate limit exceeded{reason}")

    def resolve_tracks(self, track_ids):
        """Resolve tracks concurrently emulating browser

        :param track_ids:list of track ids
        :return:list `Track`
        """
        pool = ThreadPool(processes=16)
        tracks = pool.map(self.get_track, track_ids)
        pool.close()
        return self.sanitize_tracks(tracks)
