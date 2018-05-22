from __future__ import unicode_literals

import collections
import logging
import re
import string
import time
import unicodedata
from contextlib import closing
from multiprocessing.pool import ThreadPool
from urllib import quote_plus

from mopidy import httpclient
from mopidy.models import Album, Artist, Track

import requests
from requests.exceptions import HTTPError

import mopidy_soundcloud


logger = logging.getLogger(__name__)


def safe_url(uri):
    return quote_plus(
        unicodedata.normalize('NFKD', unicode(uri)).encode('ASCII', 'ignore'))


def readable_url(uri):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    safe_uri = unicodedata.normalize('NFKD', unicode(uri)).encode('ASCII',
                                                                  'ignore')
    return re.sub('\s+', ' ',
                  ''.join(c for c in safe_uri if c in valid_chars)).strip()


def streamble_url(url, client_id):
    return '%s?client_id=%s' % (url, client_id)


def get_requests_session(proxy_config, user_agent, token):
    proxy = httpclient.format_proxy(proxy_config)
    full_user_agent = httpclient.format_user_agent(user_agent)

    session = requests.Session()
    session.proxies.update({'http': proxy, 'https': proxy})
    session.headers.update({'user-agent': full_user_agent})
    session.headers.update({'Authorization': 'OAuth %s' % token})

    return session


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
        self.explore_songs = config['soundcloud'].get('explore_songs', 10)
        self.http_client = get_requests_session(
            proxy_config=config['proxy'],
            user_agent='%s/%s' % (
                mopidy_soundcloud.SoundCloudExtension.dist_name,
                mopidy_soundcloud.__version__),
            token=config['soundcloud']['auth_token'])

    @property
    @cache()
    def user(self):
        return self._get('me')

    @cache()
    def get_user_stream(self):
        # https://developers.soundcloud.com/docs/api/reference#activities
        tracks = []
        stream = self._get('me/activities', limit=True).get('collection', [])
        for data in stream:
            kind = data.get('origin')
            # multiple types of track with same data
            if kind:
                if kind['kind'] == 'track':
                    tracks.append(self.parse_track(kind))
                elif kind['kind'] == 'playlist':
                    playlist = kind.get('tracks')
                    if isinstance(playlist, collections.Iterable):
                        tracks.extend(self.parse_results(playlist))

        return self.sanitize_tracks(tracks)

    def get_followings(self, query_user_id=None):

        if query_user_id:
            return self._get('users/%s/tracks' % query_user_id) or []

        users = []
        playlists = self._get('me/followings', limit=True)
        for playlist in playlists.get('collection', []):
            name = playlist.get('username')
            user_id = str(playlist.get('id'))
            logger.debug('Fetched user %s with id %s' % (name, user_id))
            users.append((name, user_id))
        return users

    @cache()
    def get_set(self, set_id):
        # https://developers.soundcloud.com/docs/api/reference#playlists
        playlist = self._get('playlists/%s' % set_id)
        return playlist.get('tracks', [])

    def get_sets(self):
        playable_sets = []
        for playlist in self._get('me/playlists', limit=True):
            name = playlist.get('title')
            set_id = str(playlist.get('id'))
            tracks = playlist.get('tracks')
            logger.debug('Fetched set %s with id %s (%d tracks)' % (
                name, set_id, len(tracks)
            ))
            playable_sets.append((name, set_id, tracks))
        return playable_sets

    def get_user_liked(self):
        # https://developers.soundcloud.com/docs/api/reference#GET--users--id--favorites
        likes = []
        liked = self._get('me/favorites', limit=True)
        for data in liked:
            if data['kind'] == 'track':
                likes.append(self.parse_track(data))
            else:
                likes.append((data['title'], str(data['id'])))

        return self.sanitize_tracks(likes)

    # Public
    @cache()
    def get_track(self, track_id, streamable=False):
        logger.debug('Getting info for track with id %s' % track_id)
        try:
            return self.parse_track(self._get('tracks/%s' % track_id),
                                    streamable)
        except Exception:
            return None

    def parse_track_uri(self, track):
        logger.debug('Parsing track %s' % (track))
        if hasattr(track, "uri"):
            track = track.uri
        return track.split('.')[-1]

    def search(self, query):
        # https://developers.soundcloud.com/docs/api/reference#tracks
        query = quote_plus(query.encode('utf-8'))
        search_results = self._get('tracks?q=%s' % query, limit=True)
        tracks = []
        for track in search_results:
            tracks.append(self.parse_track(track, False))
        return self.sanitize_tracks(tracks)

    def parse_results(self, res):
        tracks = []
        logger.debug('Parsing %d result item(s)...', len(res))
        for item in res:
            if item['kind'] == 'track':
                tracks.append(self.parse_track(item))
            elif item['kind'] == 'playlist':
                playlist_tracks = item.get('tracks', [])
                logger.debug('Parsing %u playlist track(s)...',
                    len(playlist_tracks))
                for track in playlist_tracks:
                    tracks.append(self.parse_track(track))
            else:
                logger.warning("Unknown item type '%s'.", item['kind'])
        return self.sanitize_tracks(tracks)

    def resolve_url(self, uri):
        return self.parse_results([self._get('resolve?url=%s' % uri)])

    def _get(self, url, limit=None):
        url = 'https://api.soundcloud.com/%s' % url
        params = {'client_id': self.CLIENT_ID}
        if limit:
            params['limit'] = self.explore_songs
        try:
            with closing(self.http_client.get(url, params=params)) as res:
                logger.debug('Requested %s', res.url)
                res.raise_for_status()
                return res.json()
        except Exception as e:
            if isinstance(e, HTTPError) and e.response.status_code == 401:
                logger.error('Invalid "auth_token" used for SoundCloud '
                             'authentication!')
            else:
                logger.error('SoundCloud API request failed: %s' % e)
        return {}

    def sanitize_tracks(self, tracks):
        return filter(None, tracks)

    @cache()
    def parse_track(self, data, remote_url=False):
        if not data:
            return None
        if not data.get('streamable'):
            logger.info(
                "'%s' can't be streamed from SoundCloud" % data.get('title'))
            return None
        if not data.get('kind') == 'track':
            logger.debug('%s is not track' % data.get('title'))
            return None

        # NOTE kwargs dict keys must be bytestrings to work on Python < 2.6.5
        # See https://github.com/mopidy/mopidy/issues/302 for details.

        track_kwargs = {}
        artist_kwargs = {}
        album_kwargs = {}

        if 'title' in data:
            label_name = data.get('label_name')
            if not label_name:
                label_name = data.get(
                    'user', {}).get('username', 'Unknown label')

            track_kwargs[b'name'] = data['title']
            artist_kwargs[b'name'] = label_name
            album_kwargs[b'name'] = 'SoundCloud'

        if 'date' in data:
            track_kwargs[b'date'] = data['date']

        if remote_url:
            track_kwargs[b'uri'] = self.get_streamble_url(data['stream_url'])
            if track_kwargs[b'uri'] is None:
                logger.info("'%s' can't be streamed "
                            "from SoundCloud" % data.get('title'))
                return None
        else:
            track_kwargs[b'uri'] = 'soundcloud:song/%s.%s' % (
                readable_url(data.get('title')), data.get('id'))

        track_kwargs[b'length'] = int(data.get('duration', 0))
        track_kwargs[b'comment'] = data.get('permalink_url', '')

        if artist_kwargs:
            track_kwargs[b'artists'] = [Artist(**artist_kwargs)]

        if album_kwargs:
            if data.get('artwork_url'):
                album_kwargs[b'images'] = [data['artwork_url']]
            else:
                image = data.get('user', {}).get('avatar_url')
                album_kwargs[b'images'] = [image]

            track_kwargs[b'album'] = Album(**album_kwargs)

        return Track(**track_kwargs)

    @cache()
    def get_streamble_url(self, url):
        req = self.http_client.head(streamble_url(url, self.CLIENT_ID))
        if req.status_code == 302:
            return req.headers.get('Location', None)
        elif req.status_code == 429:
            logger.warning('SoundCloud daily rate limit exceeded')

    def resolve_tracks(self, track_ids):
        """Resolve tracks concurrently emulating browser

        :param track_ids:list of track ids
        :return:list `Track`
        """
        pool = ThreadPool(processes=16)
        tracks = pool.map(self.get_track, track_ids)
        pool.close()
        return self.sanitize_tracks(tracks)
