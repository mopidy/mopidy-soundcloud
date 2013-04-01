Mopidy-SoundCloud
=================

Mopidy http://www.mopidy.com/ extension for playing music from
SoundCloud http://www.soundcloud.com

Usage
-----

Install by running::

    sudo pip install mopidy-soundcloud


Before starting Mopidy, you must add your SoundCloud authentication token
to the Mopidy configuration file. You can get yours at http://www.mopidy.com/authenticate

    [soundcloud]
    auth_key = "1-1111-1111111"

Extra playlists from http://www.soundcloud.com/explore can be
retrieved with explore setting. For example, if you want Smooth Jazz from 
https://soundcloud.com/explore/jazz%2Bblues your entry would be 'jazz%2Bblues/Smooth Jazz'

    [soundcloud]
    explore = 'electronic/Ambient, pop/New Wave, rock/Indie'

Project resources
-----------------

- Source code https://github.com/dz0ny/mopidy-soundcloud_
- Issue tracker https://github.com/mopidy/mopidy-soundcloud/issues
- Download development snapshot https://github.com/dz0ny/mopidy-soundcloud/tarball/develop#egg=mopidy-soundcloud-dev

License 
-------

Copyright (C) 2013 <dz0ny at shortmail dot com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.