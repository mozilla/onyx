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
