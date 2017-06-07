# Onyx

[![Build Status](https://travis-ci.org/mozilla/onyx.svg?branch=master)](https://travis-ci.org/mozilla/onyx)
[![Coverage Status](https://coveralls.io/repos/oyiptong/onyx/badge.png?branch=master)](https://coveralls.io/r/oyiptong/onyx?branch=master)

Link server and engagement metrics aggregator for Firefox Directory Links

# Install
```sh
# install Onyx in a local Python virtualenv
$ ./setup-project.sh

# run the dev server at localhost:5000
$ manage.py runserver

# ping the server
$ curl -v localhost:5000/__heartbeat__
```

# Run within docker

You can run Onyx within docker (Note: *NOT* for production).

```sh
# build the Onyx docker image locally
$ make docker

# run the container at localhost:5000
$ make run

# tail the logs
$ make log

# stop the container
$ make stop

# start the stopped container
$ make start

# remove the container
$ make clean
```

# Links

There are a few API endpoints we care about:

* [/v2/links/fetch/`locale`](#v2linksfetchlocale)
* [/v2/links/fetch](#v2linksfetch)
* [/v2/links/view](#v2linksview)
* [/v2/links/click](#v2linksclick)
* [/v3/links/fetch/`locale`/`channel`](#v3linksfetchlocalechannel)
* [/v3/links/view](#v3linksview)
* [/v3/links/click](#v3linksclick)
* [/v3/links/activity-stream](#v3linksactivity-stream)
* [/v3/links/ping-centre](#v3linksping-centre)
* [/v4/links/activity-stream](#v4linksactivity-stream)

## /v2/links/fetch/`locale`

The `fetch` endpoint takes locale from the url path and returns an `HTTP 303` redirect to a CDN location with the content appropriate for the user agent.

In Firefox, the `fetch` endpoint is called at most once daily. Firefox keeps
track of the last time it fetched, and checks at every opportunity, (e.g. when
sending a ping, when a new tab page is open, on browser start) whether or not
it should fetch again. This is guaranteed to trigger at most once daily.

Method: GET

URL Parameters:

* locale	-	User Agent locale setting

## /v2/links/fetch

__DEPRECATED__

The `fetch` endpoint takes locale in a JSON payload and returns an `HTTP 303` redirect to a CDN location with the content appropriate for the user agent.

In Firefox, the `fetch` endpoint is called at most once daily. Firefox keeps
track of the last time it fetched, and checks at every opportunity, (e.g. when
sending a ping, when a new tab page is open, on browser start) whether or not
it should fetch again. This is guaranteed to trigger at most once daily.

__Note__: Prior to having v2, the v1 of this endpoint also took a data parameter, hence why this is a POST

Method: POST

Example payload:

    {"locale": "en-US"}
    
    
Parameters:

* locale	-	User Agent locale setting


## /v2/links/view

The `view` endpoint is called each time a new tab page is opened. An asynchronous ping is sent from Firefox to Mozilla servers. The goal is to capture the impression data for tiles, in order to calculate reach and click-through rates (CTR).

Method: POST

Example Payload:

    {
      "view": 1,
      "locale": "en-US",
      "tiles": [
        {
    	  "id": 8,
          "pin": true,
          "pos": 2,
          "score": 2000,
    	  "url": ""
    	},
    	{
    	  "id": 12
    	}
      ]
    }

Parameters:
* `view`: the value of this `action` is the index of the last tile in `tiles` visible in the user's viewport
* `tiles`: an ordered array of tiles representative of what is in a new tab page
	* `id`: a tile ID. provided in the fetch payload as `directoryId`; absent for history tiles
	* `pin`: signals that the tile is pinned in the UA; absent for unpinned tiles
	* `pos`: denotes the index of the tile in the new tab page; absent if the value is the same as its array index of `tiles`
	* `score`: frecency for the tile; absent for frecencies under 5000
* `locale`: User Agent locale setting


## /v2/links/click

The `click` endpoint captures any click interaction with the tile. This includes `click`, `block`, `pin`, `unpin`, `sponsored`, and `sponsored_link`.

When the user interacts with the tile, an asynchronous ping is sent to Mozilla servers. This is to measure a click event.

Positive events (`click`, `pin`) and negative events (`block`, `unpin`) are all very important. They can tell us that certain tiles are not appropriate or that people do not like them.

Method: POST

Example Payload:

    {
      "click": 1,
      "locale": "en-US",
      "tiles": [
        {
          "id": 8,
          "pin": true,
          "pos": 2,
          "score": 2000,
          "url": ""
        },
        {
          "id": 12
        },
        ...
      ]
    }

Parameters:

* `click`/`block`/`pin`/`unpin`/`sponsored`/`sponsored_link`: Only one of these can happen in one payload. The value of this `action` is the index in `tiles` for which this action applies
* The other parameters - i.e. the `locale` and `tiles` params - are the same as for `/v2/links/view`.

## /v3/links/fetch/`locale`/`channel`

The `fetch` endpoint takes locale and channel from the url path and returns an `HTTP 303` redirect to a CDN location with the content appropriate for the user agent.

In Firefox, the `fetch` endpoint is called at most once daily. Firefox keeps
track of the last time it fetched, and checks at every opportunity, (e.g. when
sending a ping, when a new tab page is open, on browser start) whether or not
it should fetch again. This is guaranteed to trigger at most once daily.

Method: GET

URL Parameters:

* locale	-	User Agent locale setting
* channel       -       Firefox Channel the request is coming from

## /v3/links/view

unchanged from [/v2/links/view](#v2linksview)

## /v3/links/click

unchanged from [/v2/links/click](#v2linksclick)

## /v3/links/activity-stream

The `activity-stream` endpoint captures any event takes place in the Activity Stream Addon.

Method: POST

Example Payload:

    {
      "action": "activity_stream_session",
      "client_id": "some_client_id",
      "addon_version": "1.0",
      "tab_id": 1,
      "load_reason": "newtab",  #["newtab", "focus", "restore"]
      "source": "activity_stream",  #["recent_links", "recent_bookmarks", "frecent_links", "top_sites", "spotlight"]
      "search": 0,  # indicates a search was performed
      "max_scroll_depth": 100,
      "click_position": 2,  #[TBD, index of object clicked on a click event or -1? or 2D coordinates e.g. 200x400?]
      "total_bookmarks": 5,
      "total_history_size": 1000,
      "session_duration": 2000,
      "unload_reason": "click"  # ["click", "search", "close", "unfocus"]
    }

## /v3/links/ping-centre

The `ping-centre` endpoint captures any event defined in the [Ping-centre](https://github.com/mozilla/ping-centre) repo.

Method: POST

Example Payload:

    {
      "topic": "activity_stream_mobile_session",
      "client_id": "some_client_id",
      "addon_version": "1.0",
      "tab_id": 1,
      "load_reason": "newtab",
      "source": "activity_stream",
      "search": 0,  # indicates a search was performed
      "max_scroll_depth": 100,
      "click_position": 2,
      "total_bookmarks": 5,
      "total_history_size": 1000,
      "session_duration": 2000,
      "unload_reason": "click"
    }

## /v4/links/activity-stream

The `activity-stream` endpoint captures any event takes place in the Activity Stream system addon.

Method: POST

Example Payload:

    {
      "action": "activity_stream_session",
      "client_id": "some_client_id",
      "addon_version": "1.0",
      "tab_id": 1,
      "load_reason": "newtab",  #["newtab", "focus", "restore"]
      "source": "activity_stream",  #["recent_links", "recent_bookmarks", "frecent_links", "top_sites", "spotlight"]
      "search": 0,  # indicates a search was performed
      "max_scroll_depth": 100,
      "click_position": 2,  #[TBD, index of object clicked on a click event or -1? or 2D coordinates e.g. 200x400?]
      "total_bookmarks": 5,
      "total_history_size": 1000,
      "session_duration": 2000,
      "unload_reason": "click"  # ["click", "search", "close", "unfocus"]
    }
