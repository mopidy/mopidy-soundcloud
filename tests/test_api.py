import os.path
import unittest
from unittest import mock

import vcr

import mopidy_soundcloud
from mopidy.models import Track
from mopidy_soundcloud import Extension
from mopidy_soundcloud.soundcloud import SoundCloudClient, readable_url

local_path = os.path.abspath(os.path.dirname(__file__))
my_vcr = vcr.VCR(
    serializer="yaml",
    cassette_library_dir=local_path + "/fixtures",
    record_mode="once",
    match_on=["uri", "method"],
    decode_compressed_response=False,
    filter_headers=["Authorization"],
)


class ApiTest(unittest.TestCase):
    @my_vcr.use_cassette("sc-login.yaml")
    def setUp(self):
        config = Extension().get_config_schema()
        config["auth_token"] = "3-35204-970067440-lVY4FovkEcKrEGw"
        config["explore_songs"] = 10
        self.api = SoundCloudClient({"soundcloud": config, "proxy": {}})

    def test_sets_user_agent(self):
        agent = "Mopidy-SoundCloud/%s Mopidy/" % mopidy_soundcloud.__version__
        assert agent in self.api.http_client.headers["user-agent"]

    def test_public_client_no_token(self):
        token_key = "authorization"
        assert token_key not in self.api.public_stream_client.headers._store

    def test_resolves_string(self):
        _id = self.api.parse_track_uri("soundcloud:song.38720262")
        assert _id == "38720262"

    @my_vcr.use_cassette("sc-login-error.yaml")
    def test_responds_with_error(self):
        with mock.patch("mopidy_soundcloud.soundcloud.logger.error") as d:
            config = Extension().get_config_schema()
            config["auth_token"] = "1-fake-token"
            SoundCloudClient({"soundcloud": config, "proxy": {}}).user
            d.assert_called_once_with(
                'Invalid "auth_token" used for SoundCloud authentication!'
            )

    @my_vcr.use_cassette("sc-login.yaml")
    def test_returns_username(self):
        user = self.api.user.get("username")
        assert user == "Nick Steel 3"

    @my_vcr.use_cassette("sc-resolve-track.yaml")
    def test_resolves_object(self):
        trackc = {}
        trackc["uri"] = "soundcloud:song.38720262"
        track = Track(**trackc)

        id = self.api.parse_track_uri(track)
        assert id == "38720262"

    @my_vcr.use_cassette("sc-resolve-track-none.yaml")
    def test_resolves_unknown_track_to_none(self):
        track = self.api.get_parsed_track("s38720262")
        assert track is None

    @my_vcr.use_cassette("sc-resolve-track.yaml")
    def test_resolves_track(self):
        track = self.api.get_parsed_track("13158665")
        assert isinstance(track, Track)
        assert track.uri == "soundcloud:song/Munching at Tiannas house.13158665"

    @my_vcr.use_cassette("sc-resolve-http.yaml")
    def test_resolves_http_url(self):
        track = self.api.resolve_url(
            "https://soundcloud.com/bbc-radio-4/m-w-cloud"
        )[0]
        assert isinstance(track, Track)
        assert (
            track.uri
            == "soundcloud:song/That Mitchell and Webb Sound The Cloud.122889665"
        )

    @my_vcr.use_cassette("sc-resolve-set.yaml")
    def test_resolves_set_url(self):
        expected_tracks = [
            "01 Dash And Blast",
            "02 We Flood Empty Lakes",
            "03 A Song For Starlit Beaches",
            "04 Illuminate My Heart, My Darling",
        ]
        tracks = self.api.resolve_url(
            "https://soundcloud.com/yndihalda/sets/dash-and-blast"
        )
        assert len(tracks) == 4
        for i, _ in enumerate(expected_tracks):
            assert isinstance(tracks[i], Track)
            assert tracks[i].name == expected_tracks[i]
            assert tracks[i].length > 500
            assert len(tracks[i].artists) == 1
            assert list(tracks[i].artists)[0].name == "yndi halda"

    @my_vcr.use_cassette("sc-liked.yaml")
    def test_get_user_likes(self):
        tracks = self.api.get_likes()
        assert len(tracks) == 3
        assert isinstance(tracks[0], Track)
        assert tracks[1].name == "Pelican - Deny The Absolute"

    @my_vcr.use_cassette("sc-stream.yaml")
    def test_get_user_stream(self):
        tracks = self.api.get_user_stream()
        assert len(tracks) == 10
        assert isinstance(tracks[0], Track)
        assert tracks[2].name == "JW Ep 20- Jeremiah Watkins"

    @my_vcr.use_cassette("sc-following.yaml")
    def test_get_followings(self):
        users = self.api.get_followings()
        assert len(users) == 10
        assert users[0] == ("Young Legionnaire", "992503")
        assert users[1] == ("Tall Ships", "1710483")
        assert users[8] == ("Pelican Song", "27945548")
        assert users[9] == ("sleepmakeswaves", "1739693")

    @my_vcr.use_cassette("sc-user-tracks.yaml")
    def test_get_user_tracks(self):
        expected_tracks = [
            "The Wait",
            "The Cliff (Palms Remix)",
            "The Cliff (Justin Broadrick Remix)",
            "The Cliff (Vocal Version)",
            "Pelican - The Creeper",
            "Pelican - Lathe Biosas",
            "Pelican - Ephemeral",
            "Pelican - Deny the Absolute",
            "Pelican - Immutable Dusk",
            "Pelican - Strung Up From The Sky",
        ]

        tracks = self.api.get_tracks(27945548)
        for i, _ in enumerate(expected_tracks):
            assert isinstance(tracks[i], Track)
            assert tracks[i].name == expected_tracks[i]
            assert tracks[i].length > 500
            assert len(tracks[i].artists) == 1

    @my_vcr.use_cassette("sc-set.yaml")
    def test_get_set(self):
        tracks = self.api.get_set("10961826")
        assert len(tracks) == 1
        assert isinstance(tracks[0], dict)

    @my_vcr.use_cassette("sc-set-invalid.yaml")
    def test_get_invalid_set(self):
        tracks = self.api.get_set("blahblahrubbosh")
        assert tracks == []

    @my_vcr.use_cassette("sc-sets.yaml")
    def test_get_sets(self):
        sets = self.api.get_sets()
        assert len(sets) == 2
        name, set_id, tracks = sets[1]
        assert name == "Pelican"
        assert set_id == "10961826"
        assert len(tracks) == 1

    def test_readeble_url(self):
        assert "Barsuk Records" == readable_url('"@"Barsuk      Records')
        assert "_Barsuk Records" == readable_url("_Barsuk 'Records'")

    @my_vcr.use_cassette("sc-resolve-track-id.yaml")
    def test_resolves_stream_track(self):
        track = self.api.get_parsed_track("13158665", True)
        assert isinstance(track, Track)
        assert track.uri == (
            "https://cf-media.sndcdn.com/fxguEjG4ax6B.128.mp3?Policy="
            "eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiKjovL2NmLW1lZGlhLnNu"
            "ZGNkbi5jb20vZnhndUVqRzRheDZCLjEyOC5tcDMiLCJDb25kaXRpb24i"
            "OnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE2MTc3MzMy"
            "MDJ9fX1dfQ__&Signature=R6mfsrmYiPXF8Q-Eh0vsmtiqnIAkFMckw"
            "6qETd0gjJlXnxzjXq~ZiY4ClwgChjfv9e5NdID54hcSrq3jamUCuQ-Gr"
            "94WH0beJFXa9itVnV2A83~FE6Fye~ocTsVx7fzrpDFKJ80csI-QtLkV3"
            "3E06oMClsMPbjvdw3d1caFpGfkck7OCmV0Z9Jat0dYDkRfjGZF7HqGRP"
            "-upiIJ3l0cWfSyhRJ~F5o29TASJMQMQAigjCV0by9DsK2Naw1tcAW4DH"
            "YJF4oOUQkTLRwtw0B5mJXfKfFGQxjj1RSGZNFZxG0oV2nD1-svYX-Enz"
            "ldPOUBDvyUr-nNmS0wR9Qm5XsTAbQ__&Key-Pair-Id=APKAI6TU7MMX"
            "M5DG6EPQ"
        )

    @my_vcr.use_cassette("sc-resolve-track-id.yaml")
    def test_unstreamable_track(self):
        track = self.api._get("tracks/13158665")
        track["streamable"] = False
        track = self.api.parse_track(track)
        assert track is None

    @my_vcr.use_cassette("sc-resolve-app-client-id.yaml")
    def test_resolves_app_client_id(self):
        track = self.api._get("tracks/13158665")
        track["sharing"] = "private"
        track = self.api.parse_track(track, True)
        assert track.uri == (
            "https://cf-media.sndcdn.com/fxguEjG4ax6B.128.mp3?Policy="
            "eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiKjovL2NmLW1lZGlhLnNu"
            "ZGNkbi5jb20vZnhndUVqRzRheDZCLjEyOC5tcDMiLCJDb25kaXRpb24i"
            "OnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE2MTc3Mzcw"
            "ODV9fX1dfQ__&Signature=AT7ZL9gDe~34stPzDOORReIeNTbEpo~27"
            "VP-set6t-T2mIW-W1fuWW6ny4-kd5XsW7mgndht1poURixYx1bUNTJFt"
            "SX1LjjfvUaGfA5w3eDbfSHvlmh8fqIVN6RZAbCwQUbcndn8TI5Q1EPfP"
            "8Aq-DLsIdUEE~3gxIVvX-YgzDZtxRMue0eefgp5oxk5z3KbHILPAyeS-"
            "GQx4JIgMxSWaMKiG0Dx0raTNW8JFNugs9u5h62J21BxGSd6aifU9boff"
            "khg1yWR9ccqHjMdDSRGpHLSBin6iNNHRzHj9vC4cq--DexYnyLQtdZp3"
            "UlaXbFlP~-3XBMf6FLNiPbUA4HxgA__&Key-Pair-Id=APKAI6TU7MMX"
            "M5DG6EPQ"
        )

    @my_vcr.use_cassette("sc-resolve-track-id-invalid-client-id.yaml")
    def test_resolves_stream_track_invalid_id(self):
        self.api.public_client_id = "blahblahrubbosh"
        track = self.api.get_parsed_track("13158665", True)
        assert isinstance(track, Track)
        assert track.uri == (
            "https://cf-media.sndcdn.com/fxguEjG4ax6B.128.mp3?Policy="
            "eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiKjovL2NmLW1lZGlhLnNu"
            "ZGNkbi5jb20vZnhndUVqRzRheDZCLjEyOC5tcDMiLCJDb25kaXRpb24i"
            "OnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE2MTc1NDI2"
            "MDh9fX1dfQ__&Signature=SwnMkrFlBL1Es-S7DMuHLiAzYxgKdl4bk"
            "sjUny73MKN9d~54MhUzYOmgzETiERC73tyGo3iovjjk6P556J3FvAibn"
            "adM7ip5pPNT5HpyS4~xE2zCAg9s1DnDSypcUzOT6pvKKTJ3F95w6~kr3"
            "lRbRfDHsuq6O1HKB4k~NBVdTMRFhDRZJPdGg2BJFiI5M-IA-Ut5CQUJS"
            "kYNXG1kQtvIJNenAUQAuQm0iKv-um7C5YbgkdOpZC~HU49YiLcCw8T~b"
            "VYRgspxMctUQssmTg5yysD65vkQk8QVWpx9kE9kxdCL7oFqdAbv9tsgu"
            "s7~nptZlygrOVi9TIyikLsi6BeMQw__&Key-Pair-Id=APKAI6TU7MMX"
            "M5DG6EPQ"
        )

    def test_parse_fail_reason(self):
        test_reason = "Unknown"
        reason_res = self.api.parse_fail_reason(test_reason)
        assert reason_res == ""

    @my_vcr.use_cassette("sc-search.yaml")
    def test_search(self):
        tracks = self.api.search("the great descent")
        assert len(tracks) == 10
        assert isinstance(tracks[0], Track)
        assert tracks[0].name == "Turn Around (Mix1)"
