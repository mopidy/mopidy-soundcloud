*****************
Mopidy-SoundCloud
*****************

.. image:: https://pypip.in/v/Mopidy-SoundCloud/badge.png
    :target: https://crate.io/packages/Mopidy-SoundCloud/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/Mopidy-SoundCloud/badge.png
    :target: https://crate.io/packages/Mopidy-SoundCloud/
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

TODO: Write one


.. image:: https://d2weczhvl823v0.cloudfront.net/mopidy/mopidy-soundcloud/trend.png
   :alt: Bitdeli badge
   :target: https://bitdeli.com/free

