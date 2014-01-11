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


Configuration
=============

#. You must register for a user account at http://www.soundcloud.com/

#. You need a SoundCloud authentication token for Mopidy from
   http://www.mopidy.com/authenticate

#. Add the authentication token to the ``mopidy.conf`` config file::

    [soundcloud]
    auth_token = 1-1111-1111111

#. Extra playlists from http://www.soundcloud.com/explore can be retrieved by
   setting the ``soundcloud/explore`` config value. For example, if you want
   Smooth Jazz from https://soundcloud.com/explore/jazz%2Bblues your entry
   would be "jazz%2Bblues/Smooth Jazz". Example config::

    [soundcloud]
    auth_token = 1-1111-1111111
    explore = electronic/Ambient, pop/New Wave, rock/Indie


Project resources
=================

- `Source code <https://github.com/mopidy/mopidy-soundcloud>`_
- `Issue tracker <https://github.com/mopidy/mopidy-soundcloud/issues>`_
- `Download development snapshot
  <https://github.com/mopidy/mopidy-soundcloud/tarball/master#egg=Mopidy-SoundCloud-dev>`_


Changelog
=========

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
