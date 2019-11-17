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
        config["auth_token"] = "1-35204-61921957-55796ebef403996"
        config["explore_songs"] = 10
        self.api = SoundCloudClient({"soundcloud": config, "proxy": {}})

    def test_sets_user_agent(self):
        agent = "Mopidy-SoundCloud/%s Mopidy/" % mopidy_soundcloud.__version__
        assert agent in self.api.http_client.headers["user-agent"]

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
                'Invalid "auth_token" used for ' "SoundCloud authentication!"
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
        track = self.api.get_track("s38720262")
        assert track is None

    @my_vcr.use_cassette("sc-resolve-track.yaml")
    def test_resolves_track(self):
        track = self.api.get_track("13158665")
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
        track = self.api.get_track("13158665", True)
        assert isinstance(track, Track)
        assert track.uri == (
            "https://cf-media.sndcdn.com/fxguEjG4ax6B.128.mp3?Policy="
            "eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiKjovL2NmLW1lZGlhLnNu"
            "ZGNkbi5jb20vZnhndUVqRzRheDZCLjEyOC5tcDMiLCJDb25kaXRpb24i"
            "OnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE0Nzc2MDA1"
            "NTd9fX1dfQ__&Signature=u9bxAkZOtTTF1VqTmLGmw3ENrqbiSTFK-"
            "sMvZL-ZsQK85DOepHh5MfPA4MNooszUy~PZqiVyBn4YnElhWyb~4B7kS"
            "6y0VZ6t-qF78CfTMOimemafpqfWJ8nYXczhM9pUpAwiS--lkNjGks4Qx"
            "i-FZJDBPG99gAIU0eVW78CADcpuOKLugGpzHl6gRPN2Z4zZ9dVujZ5Ml"
            "G2OWnPuNiBcE~wUFwcOxt9N6ePTff-wMFQR2PGpEK6wc6bWuB4WFNBkE"
            "0bmEke4cOQjWHa5FwYEidZN5rvv5lVT1r07zzifnADEipwMaZ2-QYdqz"
            "OYaM4jymFDhl7DklaU24PY5C5mH0A__&Key-Pair-Id=APKAJAGZ7VMH"
            "2PFPW6UQ"
        )

    @my_vcr.use_cassette("sc-search.yaml")
    def test_search(self):
        tracks = self.api.search("the great descent")
        assert len(tracks) == 10
        assert isinstance(tracks[0], Track)
        assert tracks[0].name == "Turn Around (Mix1)"
