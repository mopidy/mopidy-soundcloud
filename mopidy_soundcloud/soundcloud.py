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


def get_user_url(user_id):
    if not user_id:
        return 'me'
    else:
        return 'users/%s' % user_id


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
        self.explore_songs = config['soundcloud'].get('explore_songs', 25)
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

    @cache(ttl=10)
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

    @cache(ttl=10)
    def get_followings(self, user_id=None):
        user_url = get_user_url(user_id)
        users = []
        playlists = self._get('%s/followings' % user_url, limit=True)
        for playlist in playlists.get('collection', []):
            user_name = playlist.get('username')
            user_id = str(playlist.get('id'))
            logger.debug('Fetched user %s with id %s' % (user_name, user_id))
            users.append((user_name, user_id))
        return users

    @cache()
    def get_set(self, set_id):
        # https://developers.soundcloud.com/docs/api/reference#playlists
        playlist = self._get('playlists/%s' % set_id)
        return playlist.get('tracks', [])

    @cache(ttl=10)
    def get_sets(self, user_id=None):
        user_url = get_user_url(user_id)
        playable_sets = []
        for playlist in self._get('%s/playlists' % user_url, limit=True):
            name = playlist.get('title')
            set_id = str(playlist.get('id'))
            tracks = playlist.get('tracks', [])
            logger.debug('Fetched set %s with id %s (%d tracks)' % (
                name, set_id, len(tracks)
            ))
            playable_sets.append((name, set_id, tracks))
        return playable_sets

    @cache(ttl=10)
    def get_likes(self, user_id=None):
        # https://developers.soundcloud.com/docs/api/reference#GET--users--id--favorites
        user_url = get_user_url(user_id)
        likes = self._get('%s/favorites' % user_url, limit=True)
        return self.parse_results(likes)

    @cache(ttl=10)
    def get_tracks(self, user_id=None):
        user_url = get_user_url(user_id)
        tracks = self._get('%s/tracks' % user_url, limit=True)
        return self.parse_results(tracks)

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
        params = [('client_id', self.CLIENT_ID)]
        if limit:
            params.insert(0, ('limit', self.explore_songs))
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

        track_kwargs = {}
        artist_kwargs = {}
        album_kwargs = {}

        if 'title' in data:
            label_name = data.get('label_name')
            if not label_name:
                label_name = data.get(
                    'user', {}).get('username', 'Unknown label')

            track_kwargs['name'] = data['title']
            artist_kwargs['name'] = label_name
            album_kwargs['name'] = 'SoundCloud'

        if 'date' in data:
            track_kwargs['date'] = data['date']

        if remote_url:
            track_kwargs['uri'] = self.get_streamble_url(data['stream_url'])
            if track_kwargs['uri'] is None:
                logger.info("'%s' can't be streamed "
                            "from SoundCloud" % data.get('title'))
                return None
        else:
            track_kwargs['uri'] = 'soundcloud:song/%s.%s' % (
                readable_url(data.get('title')), data.get('id'))

        track_kwargs['length'] = int(data.get('duration', 0))
        track_kwargs['comment'] = data.get('permalink_url', '')

        if artist_kwargs:
            track_kwargs['artists'] = [Artist(**artist_kwargs)]

        if album_kwargs:
            if data.get('artwork_url'):
                album_kwargs['images'] = [data['artwork_url']]
            else:
                image = data.get('user', {}).get('avatar_url')
                album_kwargs['images'] = [image]
            if len(album_kwargs['images']) == 1:
                image = album_kwargs['images'][0].replace('large', 't500x500')
                album_kwargs['images'] = [image]

            track_kwargs['album'] = Album(**album_kwargs)

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
