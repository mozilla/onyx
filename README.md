# onyx

[![Build Status](https://travis-ci.org/oyiptong/onyx.svg?branch=master)](https://travis-ci.org/oyiptong/onyx)
[![Coverage Status](https://coveralls.io/repos/oyiptong/onyx/badge.png?branch=master)](https://coveralls.io/r/oyiptong/onyx?branch=master)

Link server and engagement metrics aggregator for Firefox Directory Links

There are a few API endpoints we care about:

* /v2/links/fetch/`locale`
* /v2/links/fetch
* /v2/links/click
* /v2/links/view

## /v2/links/fetch/`locale`

The `fetch` endpoint takes locale in a JSON payload and returns an `HTTP 303` redirect to a CDN location with the content appropriate for the user agent.

In Firefox, this is called when the `idle-daily` event is triggered. This is guaranteed to trigger only once daily.

Method: GET

## /v2/links/fetch

__DEPRECATED__

The `fetch` endpoint takes locale in a JSON payload and returns an `HTTP 303` redirect to a CDN location with the content appropriate for the user agent.

In Firefox, this is called when the `idle-daily` event is triggered. This is guaranteed to trigger only once daily.

__Note__: Prior to having v2, the v1 of this endpoint also took a data parameter, hence why this is a POST

Method: POST

Example payload:

    {"locale": "en-US"}
    
    
Parameters:

* locale	-	User Agent locale setting


## /v2/links/view

The `view` endpoint is called each time a new tab page is opened. An asynchronous ping is sent from Firefox to Mozilla servers. The goal is to capture the impression data for tiles, in order to calculate raech and click-through rates (CTR).

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
	* `url`: signals that the tile is enhanced (with an empty "" value); absent for directory and history tiles
* `locale`: User Agent locale setting


## /v2/links/click

The `click` endpoint captures any click interaction with the tile. This includes `click`, `block`, `pin`, `unpin`, `sponsored`, and `sponsored_link`.

When the user interacts with the tile, an asynchronous ping is sent to Mozilla servers. This is to measure a click event. Since our business model is Cost per Click (CPC), this metric is vital.

Positive events and perhaps more importantly, negative events like `block` and `unpin` are also very important. It can tell us that certain tiles are not appropriate or that people do not like them.

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
* The rest of the parameters are the same as for `/v2/links/view` except for the `view` action, i.e. the `locale` and `tiles` params.
