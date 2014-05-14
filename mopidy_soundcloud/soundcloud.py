from __future__ import unicode_literals
import logging
import re
import string
import time
from urllib import quote_plus
import collections
import unicodedata

import requests

from mopidy.models import Track, Artist, Album


logger = logging.getLogger(__name__)


def safe_url(uri):
    return quote_plus(unicodedata.normalize(
        'NFKD',
        unicode(uri)
    ).encode('ASCII', 'ignore'))


def readable_url(uri):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    safe_uri = unicodedata.normalize(
        'NFKD',
        unicode(uri)
    ).encode('ASCII', 'ignore')
    return re.sub(
        '\s+',
        ' ',
        ''.join(c for c in safe_uri if c in valid_chars)
    ).strip()


class cache(object):
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


class SoundCloudClient(object):
    CLIENT_ID = '93e33e327fd8a9b77becd179652272e2'

    def __init__(self, config):
        super(SoundCloudClient, self).__init__()
        token = config['auth_token']
        self.explore_songs = config['explore_songs']
        self.http_client = requests.Session()
        self.http_client.headers.update({'Authorization': 'OAuth %s' % token})

    @property
    @cache()
    def user(self):
        return self._get('me.json')

    @cache()
    def get_user_stream(self):
        # User timeline like playlist which uses undocumented api
        # https://api.soundcloud.com/e1/me/stream.json?offset=0
        # returns five elements per request
        tracks = []
        for sid in xrange(0, 2):
            stream = self._get('e1/me/stream.json?offset=%s' % sid * 5)
            for data in stream.get('collection'):
                kind = data.get('type')
                # multiple types of track with same data
                if 'track' in kind:
                    tracks.append(self.parse_track(data.get('track')))
                if kind == 'playlist':
                    playlist = data.get('playlist').get('tracks')
                    if isinstance(playlist, collections.Iterable):
                        tracks.extend(self.parse_results())

        return self.sanitize_tracks(tracks)

    def get_explore(self, query_explore_id=None):
        explore = self._get('/explore/v2')
        if query_explore_id:
            urn = explore.get('categories').get('music')[int(query_explore_id)]
            web_tracks = self._get(
                'explore/%s?tag=%s&limit=%s&offset=0&linked_partitioning=1' %
                (urn, quote_plus(explore.get('tag')), self.explore_songs),
                'api-v2'
            )
            tracks = []
            for track in web_tracks.get('tracks'):
                tracks.append(self.get_track(track.get('id')))
            return tracks

        return explore.get('categories').get('music')

    def get_groups(self, query_group_id=None):

        if query_group_id:
            web_tracks = self._get('groups/%d/tracks.json' % int(
                query_group_id))
            tracks = []
            for track in web_tracks:
                if 'track' in track.get('kind'):
                    tracks.append(self.parse_track(track))
            return tracks
        else:
            return self._get('me/groups.json')

    def get_followings(self, query_user_id=None):

        if query_user_id:
            return self._get('users/%s/tracks.json' % query_user_id)

        users = []
        for playlist in self._get('me/followings.json?limit=1000'):
            name = playlist.get('username')
            user_id = str(playlist.get('id'))
            logger.debug(
                'Fetched user %s with id %s' % (
                    name, user_id
                )
            )

            users.append((name, user_id))
        return users

    @cache()
    def get_set(self, set_id):
        playlist = self._get('playlists/%s.json' % set_id)
        return playlist.get('tracks', [])

    def get_sets(self):
        playable_sets = []
        for playlist in self._get('me/playlists.json?limit=1000'):
            name = playlist.get('title')
            set_id = str(playlist.get('id'))
            tracks = playlist.get('tracks')
            logger.debug(
                'Fetched set %s with id %s (%d tracks)' % (
                    name, set_id, len(tracks)
                )
            )
            playable_sets.append((name, set_id, tracks))
        return playable_sets

    def get_user_liked(self):
        # Note: As with get_user_stream, this API call is undocumented.
        likes = []
        liked = self._get('e1/me/likes.json?limit=1000')
        for data in liked:

            track = data['track']
            if track:
                likes.append(self.parse_track(track))

            pl = data['playlist']
            if pl:
                likes.append((pl['title'], str(pl['id'])))

        return likes

    # Public
    @cache()
    def get_track(self, track_id, streamable=False):
        logger.debug('Getting info for track with id %s' % track_id)
        try:
            return self.parse_track(
                self._get('tracks/%s.json' % track_id),
                streamable
            )
        except Exception:
            logger.info('Song %s was removed' % track_id)
            return Track()

    def parse_track_uri(self, track):
        logger.debug('Parsing track %s' % (track))
        if hasattr(track, "uri"):
            track = track.uri
        return track.split('.')[-1]

    def search(self, query):

        search_results = self._get(
            'tracks.json?q=%s&filter=streamable&order=hotness&limit=10' %
            quote_plus(query)
        )
        tracks = []
        for track in search_results:
            tracks.append(self.parse_track(track, False))
        return self.sanitize_tracks(tracks)

    def parse_results(self, res):
        tracks = []
        for track in res:
            tracks.append(self.parse_track(track))
        return self.sanitize_tracks(tracks)

    def resolve_url(self, uri):
        return self.parse_results([self._get('resolve.json?url=%s' % uri)])

    def _get(self, url, endpoint='api'):
        if '?' in url:
            url = '%s&client_id=%s' % (url, self.CLIENT_ID)
        else:
            url = '%s?client_id=%s' % (url, self.CLIENT_ID)

        url = 'https://%s.soundcloud.com/%s' % (endpoint, url)

        logger.info('Requesting %s' % url)
        res = self.http_client.get(url)
        res.raise_for_status()
        return res.json()

    def sanitize_tracks(self, tracks):
        return filter(None, tracks)

    @cache()
    def parse_track(self, data, remote_url=False):
        if not data:
            return []
        if not data['streamable']:
            logger.info(
                "'%s' can't be streamed from SoundCloud" % data.get('title')
            )
            return []
        if not data['kind'] == 'track':
            logger.debug('%s is not track' % data.get('title'))
            return []

        # NOTE kwargs dict keys must be bytestrings to work on Python < 2.6.5
        # See https://github.com/mopidy/mopidy/issues/302 for details.

        track_kwargs = {}
        artist_kwargs = {}
        album_kwargs = {}

        if 'title' in data:
            name = data['title']
            label_name = data.get('label_name')

            if bool(label_name):
                track_kwargs[b'name'] = name
                artist_kwargs[b'name'] = label_name
            else:
                track_kwargs[b'name'] = name
                artist_kwargs[b'name'] = data.get('user').get('username')

            album_kwargs[b'name'] = 'SoundCloud'

        if 'date' in data:
            track_kwargs[b'date'] = data['date']

        if remote_url:
            if not self.can_be_streamed(data['stream_url']):
                logger.info(
                    "'%s' can't be streamed from SoundCloud" %
                    data.get('title'))
                return []
            track_kwargs[b'uri'] = self.get_streamble_url(data['stream_url'])
        else:
            track_kwargs[b'uri'] = 'soundcloud:song/%s.%s' % (
                readable_url(data.get('title')), data.get('id')
            )

        track_kwargs[b'length'] = int(data.get('duration', 0))
        track_kwargs[b'comment'] = data.get('permalink_url', '')

        if artist_kwargs:
            artist = Artist(**artist_kwargs)
            track_kwargs[b'artists'] = [artist]

        if album_kwargs:
            if 'artwork_url' in data and data['artwork_url']:
                album_kwargs[b'images'] = [data['artwork_url']]
            else:
                image = data.get('user').get('avatar_url')
                album_kwargs[b'images'] = [image]

            album = Album(**album_kwargs)
            track_kwargs[b'album'] = album

        track = Track(**track_kwargs)
        print track
        return track

    @cache()
    def can_be_streamed(self, url):
        req = self.http_client.head(self.get_streamble_url(url))
        return req.status_code == 302

    def get_streamble_url(self, url):
        return '%s?client_id=%s' % (url, self.CLIENT_ID)
