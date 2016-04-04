1.4.19
======

* Extract action field from activity stream payload

1.4.18
======

* Upgrade gevent to 1.1.0 to fix the ssl issue

1.4.17
======

* Issue #35 - Add endpoint for Activity Stream

1.4.16
======

* Issue #33 - Add support for multiple distributions

1.4.15
======

* Bug 1184208 - Update automated tests for onyx/splice to include `hello` channel

1.4.14
======

* Bug 1182602 - Set CORS allow-origin header for fetch endpoint

1.4.13
======

* ensure update loop requests are correct and executed in the right order

1.4.12
======

* Handle errors better in the downloader code and improve monitoring scripts

1.4.11
======

* Monitoring test improvements: working geoip test + faster external_api_test

1.4.10
======

* fix verification scripts to make sure v2 endpoints are only for the `desktop` channel

1.4.9
=====

* write script for testing fetch responses with geoip handling

1.4.8
=====

* fix verification scripts to call using release names

1.4.7
=====

* add new indexes to verification script

1.4.6
=====

* Bug 1159920 - Refactor onyx to read the tile index directly from the origin

__note__:
* Requires a change in puppet scripts:
 * TILE_INDEX_FILES now takes urls instead of file paths

1.4.5
=====

* Bug 1171112 - Obtain and serve tiles for multiple channels 

__note__:
* This will require a change in puppet scripts:
  * there are additional S3 tile index origins
  * will require puppet template changes, due to cfg change to allow for multiple indexes
  * cron job will need to download 3 files instead of just 1

1.4.4
=====

* disable urllib3 warnings in external_api_test.py

1.4.3
=====

* Add grequests back to requirements.txt

1.4.2
=====

* Ensure all API endpoints contain no contents

1.4.1
=====

* Heartbeat API endpoint
* external api test script for validating fetch api

1.4.0
=====

* v3 API implemented. New functionality: serving adgroups

__note__:
This change requires a new tile index file format. The one used prior to 1.4.0 will break onyx.

1.3.7
=====

* fix travis-ci builds and make them faster

1.3.6
=====

* new feature: command line tool to flood user event log
