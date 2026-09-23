# mopidy-soundcloud

[![Latest PyPI version](https://img.shields.io/pypi/v/mopidy-soundcloud)](https://pypi.org/p/mopidy-soundcloud)
[![CI build status](https://img.shields.io/github/actions/workflow/status/mopidy/mopidy-soundcloud/ci.yml)](https://github.com/mopidy/mopidy-soundcloud/actions/workflows/ci.yml)
[![Test coverage](https://img.shields.io/codecov/c/gh/mopidy/mopidy-soundcloud)](https://codecov.io/gh/mopidy/mopidy-soundcloud)

[Mopidy](https://mopidy.com/) extension for playing music from
[SoundCloud](https://soundcloud.com/).


## Status: Authentication is broken

SoundCloud has changed how apps authenticate. Because of this, the
authentication page at https://mopidy.com/authenticate no longer gives you a
working token, and SoundCloud can reject tokens that worked before. Until this
extension supports SoundCloud's new authentication, you cannot use it with your
SoundCloud account.

For details, see
[#138](https://github.com/mopidy/mopidy-soundcloud/issues/138) and
[#123](https://github.com/mopidy/mopidy-soundcloud/issues/123).


## Maintainer wanted

Mopidy-SoundCloud is currently kept on life support by the Mopidy core
developers. It is in need of a more dedicated maintainer.

If you want to be the maintainer of Mopidy-SoundCloud, please:

1.  Make 2-3 good pull requests improving any part of the project.

2.  Read and get familiar with all of the project's open issues.

3.  Send a pull request removing this section and adding yourself as the
    "Current maintainer" in the "Credits" section below. In the pull
    request description, please refer to the previous pull requests and
    state that you've familiarized yourself with the open issues.

    As a maintainer, you'll be given push access to the repo and the
    authority to make releases to PyPI when you see fit.


## Installation

Install by running:

```sh
python3 -m pip install mopidy-soundcloud
```

See https://mopidy.com/ext/soundcloud/ for alternative installation methods.


## Configuration

First, you must register for a user acconut at https://soundcloud.com/.

Second, you need a SoundCloud authentication token for Mopidy from
https://mopidy.com/authenticate.
   
Lastly, add the authentication token to the `mopidy.conf` config file:

```ini
[soundcloud]
auth_token = 1-1111-1111111
explore_songs = 25
```

Use `explore_songs` to restrict the number of items returned.


## Troubleshooting

If you're having trouble with audio playback from SoundCloud, make sure you have
the "ugly" plugin set from GStreamer installed for MP3 support. The package is
typically named `gstreamer1.0-plugins-ugly` or similar, depending on OS and
distribution. The package isn't a strict requirement for Mopidy's core, so you
may be missing it.


## Project resources

- [Source code](https://github.com/mopidy/mopidy-soundcloud)
- [Issues](https://github.com/mopidy/mopidy-soundcloud/issues)
- [Releases](https://github.com/mopidy/mopidy-soundcloud/releases)


## Development

### Set up development environment

Clone the repo using, e.g. using [gh](https://cli.github.com/):

```sh
gh repo clone mopidy/mopidy-soundcloud
```

Enter the directory, and install dependencies using [uv](https://docs.astral.sh/uv/):

```sh
cd mopidy-soundcloud/
uv sync
```

### Running tests

To run all tests and linters in isolated environments, use
[tox](https://tox.wiki/):

```sh
tox
```

To only run tests, use [pytest](https://pytest.org/):

```sh
pytest
```

To format the code, use [ruff](https://docs.astral.sh/ruff/):

```sh
ruff format .
```

To check for lints with ruff, run:

```sh
ruff check .
```

To check for type errors, use [pyright](https://microsoft.github.io/pyright/):

```sh
pyright .
```


### Making a release

To make a release to PyPI, go to the project's [GitHub releases
page](https://github.com/mopidy/mopidy-soundcloud/releases)
and click the "Draft a new release" button.

In the "choose a tag" dropdown, select the tag you want to release or create a
new tag, e.g. `v0.1.0`. Add a title, e.g. `v0.1.0`, and a description of the changes.

Decide if the release is a pre-release (alpha, beta, or release candidate) or
should be marked as the latest release, and click "Publish release".

Once the release is created, the `release.yml` GitHub Action will automatically
build and publish the release to
[PyPI](https://pypi.org/project/mopidy-soundcloud/).


## Credits

- Original author: [Janez Troha](https://github.com/mopidy)
- Current maintainer: None. Maintainer wanted, see section above.
- [Contributors](https://github.com/mopidy/mopidy-soundcloud/graphs/contributors)
