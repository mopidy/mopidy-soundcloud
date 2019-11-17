*****************
Mopidy-SoundCloud
*****************

.. image:: https://img.shields.io/pypi/v/Mopidy-SoundCloud
    :target: https://pypi.org/project/Mopidy-SoundCloud/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/circleci/build/gh/mopidy/mopidy-soundcloud
    :target: https://circleci.com/gh/mopidy/mopidy-soundcloud
    :alt: CircleCI build status

.. image:: https://img.shields.io/codecov/c/gh/mopidy/mopidy-soundcloud
    :target: https://codecov.io/gh/mopidy/mopidy-soundcloud
    :alt: Test coverage

`Mopidy <https://mopidy.com/>`_ extension for playing music from
`SoundCloud <https://soundcloud.com>`_.


Maintainer wanted
=================

Mopidy-SoundCloud is currently kept on life support by the Mopidy core
developers. It is in need of a more dedicated maintainer.

If you want to be the maintainer of Mopidy-SoundCloud, please:

1. Make 2-3 good pull requests improving any part of the project.

2. Read and get familiar with all of the project's open issues.

3. Send a pull request removing this section and adding yourself as the
   "Current maintainer" in the "Credits" section below. In the pull request
   description, please refer to the previous pull requests and state that
   you've familiarized yourself with the open issues.

As a maintainer, you'll be given push access to the repo and the authority to
make releases to PyPI when you see fit.


Installation
============

Debian/Ubuntu/Raspbian: Install the ``mopidy-soundcloud`` package from
`apt.mopidy.com <https://apt.mopidy.com/>`_::

    sudo apt install mopidy-soundcloud

Arch Linux: Install the ``mopidy-soundcloud`` package from
`AUR <https://aur.archlinux.org/packages/mopidy-soundcloud/>`_::

    yay -S mopidy-soundcloud

OS X: Install the ``mopidy-soundcloud`` package from the
`mopidy/mopidy <https://github.com/mopidy/homebrew-mopidy>`_ Homebrew tap::

    brew install mopidy-soundcloud

Else: Install the dependencies listed above yourself, and then install the
package from PyPI::

    python3 -m pip install Mopidy-SoundCloud

If you're having trouble with audio playback from SoundCloud, make sure you
have the "ugly" plugin set from GStreamer installed for MP3 support. The
package is typically named ``gstreamer1.0-plugins-ugly`` or similar, depending
on OS and distribution. The package isn't a strict requirement for Mopidy's
core, so you may be missing it.


Configuration
=============

#. You must register for a user account at https://soundcloud.com/

#. You need a SoundCloud authentication token for Mopidy from
   https://mopidy.com/authenticate

#. Add the authentication token to the ``mopidy.conf`` config file::

    [soundcloud]
    auth_token = 1-1111-1111111
    explore_songs = 25

#. Use ``explore_songs`` to restrict the number of items returned.


Project resources
=================

- `Source code <https://github.com/mopidy/mopidy-soundcloud>`_
- `Issue tracker <https://github.com/mopidy/mopidy-soundcloud/issues>`_
- `Changelog <https://github.com/mopidy/mopidy-soundcloud/blob/master/CHANGELOG.rst>`_


Credits
=======

- Original author: `Janez Troha <https://github.com/dz0ny>`_
- Current maintainer: None. Maintainer wanted, see section above.
- `Contributors <https://github.com/mopidy/mopidy-soundcloud/graphs/contributors>`_
