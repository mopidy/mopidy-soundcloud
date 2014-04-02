*****************
Mopidy-SoundCloud
*****************

.. image:: https://pypip.in/v/Mopidy-SoundCloud/badge.png
    :target: https://pypi.python.org/pypi/Mopidy-SoundCloud/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/Mopidy-SoundCloud/badge.png
    :target: https://pypi.python.org/pypi/Mopidy-SoundCloud/
    :alt: Number of PyPI downloads

.. image:: https://travis-ci.org/mopidy/mopidy-soundcloud.png?branch=master
    :target: https://travis-ci.org/mopidy/mopidy-soundcloud
    :alt: Travis CI build status

.. image:: https://coveralls.io/repos/mopidy/mopidy-soundcloud/badge.png?branch=master
   :target: https://coveralls.io/r/mopidy/mopidy-soundcloud?branch=master
   :alt: Test coverage

`Mopidy <http://www.mopidy.com/>`_ extension for playing music from
`SoundCloud <http://www.soundcloud.com>`_.


Installation
============

Install by running::

    pip install Mopidy-SoundCloud

Or, if available, install the Debian/Ubuntu package from `apt.mopidy.com
<http://apt.mopidy.com/>`_.

If you're having trouble with audio playback from SoundCloud, make sure you
have the "ugly" plugin set from GStreamer installed for MP3 support. The
package is typically named ``gstreamer0.10-plugins-ugly`` or similar, depending
on OS and distribution. The package isn't a strict requirement for Mopidy's
core, so you may be missing it.


Configuration
=============

#. You must register for a user account at http://www.soundcloud.com/

#. You need a SoundCloud authentication token for Mopidy from
   http://www.mopidy.com/authenticate

#. Add the authentication token to the ``mopidy.conf`` config file::

    [soundcloud]
    auth_token = 1-1111-1111111
    explore_songs = 25

Project resources
=================

- `Source code <https://github.com/mopidy/mopidy-soundcloud>`_
- `Issue tracker <https://github.com/mopidy/mopidy-soundcloud/issues>`_
- `Download development snapshot
  <https://github.com/mopidy/mopidy-soundcloud/archive/master.tar.gz#egg=Mopidy-SoundCloud-dev>`_


Changelog
=========

v1.2.3 (2014-04-02)
-------------------

- Add support for playing music from groups

v1.2.2 (2014-03-26)
-------------------

- Update Soundcloud API endpoint

v1.2.1 (2014-02-21)
-------------------

- Properly escape unsafe chars in URIs.

v1.2.0 (2014-02-16)
-------------------

- Deprecated ``explore`` and ``explore_pages`` config values.

- Extension is now using Mopidy's virtual filesystem to expose music from your
  SoundCloud account instead of fake playlists. See the "Browse" or "Files"
  option in your MPD client.

  In the virtual file system you can browse:

  - The "Stream" with tracks from the users you follow.

  - All "Explore" sections.

  - Your followers and their shared tracks.

  - Your liked tracks.

  - Your sets.

- Add search support.

- Add support for looking up music by SoundCloud URLs through searching for the
  URL as a file name.

v1.1.0 (2014-01-20)
-------------------

- Updated extension and backend APIs to match Mopidy 0.18.

v1.0.18 (2014-01-11)
--------------------

- Use proper logger namespaced to ``mopidy_soundcloud`` instead of ``mopidy``.

- Fix wrong use of ``raise`` when the SoundCloud API doesn't respond as
  expected.

v1.0.17 (2013-12-21)
--------------------

- Don't cache the user request.

- Require Requests >= 2.0. (Fixes #3)

v1.0.16 (2013-10-22)
--------------------

- Require Mopidy >= 0.14.

- Fix crash when SoundCloud returns 404 on track lookup. (Fixes #7)

- Add some tests.

v1.0.15 (2013-07-31)
--------------------

- Import code from old repo.

- Handle authentication errors without crashing. (Fixes #3 and #4)
