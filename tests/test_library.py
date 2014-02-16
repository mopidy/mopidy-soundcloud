from __future__ import unicode_literals

import unittest
from mopidy.models import Ref
import pykka
from mopidy_soundcloud import actor, SoundCloudExtension
from mopidy_soundcloud.library import SoundCloudLibraryProvider


class ApiTest(unittest.TestCase):

    def setUp(self):
        config = SoundCloudExtension().get_config_schema()
        config['auth_token'] = '1-35204-61921957-55796ebef403996'
        self.backend = actor.SoundCloudBackend.start(
            config={'soundcloud': config}, audio=None).proxy()
        self.library = SoundCloudLibraryProvider(backend=self.backend)

    def tearDown(self):
        pykka.ActorRegistry.stop_all()

    def test_add_folder(self):
        self.assertEquals(
            self.library.new_folder('Test', ['test']),
            Ref(name=u'Test', type=u'directory',
                uri=b'soundcloud:directory:test')
        )

    def test_default_folders(self):
        self.assertEquals(
            self.library.browse('soundcloud:directory'),
            [
                Ref(name=u'Explore', type=u'directory',
                    uri=b'soundcloud:directory:explore'),
                Ref(name=u'Following', type=u'directory',
                    uri=b'soundcloud:directory:following'),
                Ref(name=u'Liked', type=u'directory',
                    uri=b'soundcloud:directory:liked'),
                Ref(name=u'Sets', type=u'directory',
                    uri=b'soundcloud:directory:sets'),
                Ref(name=u'Stream', type=u'directory',
                    uri=b'soundcloud:directory:stream')
            ]
        )
