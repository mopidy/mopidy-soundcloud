*********
Changelog
*********


v3.0.0 (2019-12-22)
===================

- Depend on final release of Mopidy 3.0.0.


v3.0.0rc1 (2019-11-17)
======================

- Require Mopidy >= 3.0.0a5, which required the following changes: (PR #109)

  - Stop using removed ``Album.images`` field.

- Require Python >= 3.7. No major changes required. (PR #109)

- Rate limit requests to SoundCloud. (Contributes towards fixing #99, PR #104)

- Update project setup. (PR #109)


v2.1.0 (2018-05-30)
===================

- Fix ``AttributeError: 'list' object has no attribute 'name'`` when browsing
  tracks. (Fixes #43, #45, #59, PR #69)
- Improved error handling. (Fixes #53, #71, #90, #95, PR #100)
- Merged oustanding pull requests implementing various API updates. (Fixes #79,
  #82, PR #100)
- Cached main API endpoint responses for 10 seconds.
- Cached stream links to reduce impact of API rate limit. (PR #100)
- Add ``explore_songs`` config to limit the number of results returned.
  (PR #100)


v2.0.2 (2016-01-03)
===================

- Handle HTTP connection errors without a response. (PR #61)

- Ignore tracks without an URI. (Related to mopidy#1340, PR #62)


v2.0.1 (2015-10-06)
===================

- Fix Unicode escape sequences in SoundCloud search queries by encoding as
  UTF-8. (Fixes #42, PR #55)


v2.0.0 (2015-03-25)
===================

- Require Mopidy >= 1.0.

- Update to work with new playback API in Mopidy 1.0.

- Update to work with new backend search API in Mopidy 1.0.


v1.2.5 (2014-06-24)
===================

- Add support for new explore api


v1.2.4 (2014-05-15)
===================

- Add support for adding track by url
- Fix search parsing
- Support for adding playlists from liked section
- Fix for track parsing and empty artists field


v1.2.3 (2014-04-02)
===================

- Add support for playing music from groups


v1.2.2 (2014-03-26)
===================

- Update Soundcloud API endpoint


v1.2.1 (2014-02-21)
===================

- Properly escape unsafe chars in URIs.


v1.2.0 (2014-02-16)
===================

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
===================

- Updated extension and backend APIs to match Mopidy 0.18.


v1.0.18 (2014-01-11)
====================

- Use proper logger namespaced to ``mopidy_soundcloud`` instead of ``mopidy``.

- Fix wrong use of ``raise`` when the SoundCloud API doesn't respond as
  expected.


v1.0.17 (2013-12-21)
====================

- Don't cache the user request.

- Require Requests >= 2.0. (Fixes #3)


v1.0.16 (2013-10-22)
====================

- Require Mopidy >= 0.14.

- Fix crash when SoundCloud returns 404 on track lookup. (Fixes #7)

- Add some tests.


v1.0.15 (2013-07-31)
====================

- Import code from old repo.

- Handle authentication errors without crashing. (Fixes #3 and #4)
