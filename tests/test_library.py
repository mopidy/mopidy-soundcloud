import unittest

import pykka

from mopidy.models import Ref
from mopidy_soundcloud import Extension, actor
from mopidy_soundcloud.library import (
    SoundCloudLibraryProvider,
    new_folder,
    simplify_search_query,
)
from mopidy_soundcloud.soundcloud import safe_url


class ApiTest(unittest.TestCase):
    def setUp(self):
        config = Extension().get_config_schema()
        config["auth_token"] = "1-35204-61921957-55796ebef403996"
        # using this user http://maildrop.cc/inbox/mopidytestuser
        self.backend = actor.SoundCloudBackend.start(
            config={"soundcloud": config, "proxy": {}}, audio=None
        ).proxy()
        self.library = SoundCloudLibraryProvider(backend=self.backend)

    def tearDown(self):
        pykka.ActorRegistry.stop_all()

    def test_add_folder(self):
        assert new_folder("Test", ["test"]) == Ref(
            name="Test", type="directory", uri="soundcloud:directory:test"
        )

    def test_mpc_search(self):
        assert (
            simplify_search_query({"any": ["explosions in the sky"]})
            == "explosions in the sky"
        )

    def test_moped_search(self):
        assert (
            simplify_search_query(
                {
                    "track_name": ["explosions in the sky"],
                    "any": ["explosions in the sky"],
                }
            )
            == "explosions in the sky explosions in the sky"
        )

    def test_simple_search(self):
        assert (
            simplify_search_query("explosions in the sky")
            == "explosions in the sky"
        )

    def test_aria_search(self):
        assert (
            simplify_search_query(["explosions", "in the sky"])
            == "explosions in the sky"
        )

    def test_only_resolves_soundcloud_uris(self):
        assert (
            self.library.search(
                {"uri": "http://www.youtube.com/watch?v=wD6H6Yhluo8"}
            )
            is None
        )

    def test_returns_url_safe_string(self):
        assert (
            safe_url("Alternative/Indie/rock/pop ")
            == "Alternative%2FIndie%2Frock%2Fpop+"
        )
        assert (
            safe_url("D∃∃P Hau⑀ iNDiE DᴬNCE | №➊ ²⁰¹⁴")
            == "DP+Hau+iNDiE+DANCE+%7C+No+2014"
        )

    def test_default_folders(self):
        assert self.library.browse("soundcloud:directory") == [
            Ref(
                name="Following",
                type="directory",
                uri="soundcloud:directory:following",
            ),
            Ref(
                name="Liked", type="directory", uri="soundcloud:directory:liked"
            ),
            Ref(name="Sets", type="directory", uri="soundcloud:directory:sets"),
            Ref(
                name="Stream",
                type="directory",
                uri="soundcloud:directory:stream",
            ),
        ]
