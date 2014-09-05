# onyx

Link server and engagement metrics aggregator for Firefox Directory Links

There are 3 API endpoints we care about:

* /v2/links/fetch
* /v2/links/click
* /v2/links/view

## /v2/links/fetch

The `fetch` endpoint takes locale in a JSON payload and returns an `HTTP 303` redirect to a CDN location with the content appropriate for the user agent.

In Firefox, this is called when the `idle-daily` event is triggered. This is guaranteed to trigger only once daily.

__Note__: Prior to having v2, the v1 of this endpoint also took a data parameter, hence why this is a POST. in v3, this will in all likelihood be a GET and will return a data payload instead of being a redirect.

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
      "tiles": [
        {
    	  "id": 8,
          "pin": true, # if the tile is pinned, absent otherwise
          "pos": 2,
          "score": 2000,
    	  "url": "" # present if the tile is an enhanced tile
    	},
    	{
    	  "id": 12
    	}
      ]
    }

Parameters:
* `tiles`: an ordered array of tiles representative of what is in a new tab page
	* `id`: a tile ID. provided in the fetch payload as `directoryId`
	* `pin`: signals that the tile is pinned in the UA, otherwise absent
	* `pos`: if any tiles were skipped in this payload, this denotes the index of the tile in the new tab page
	* `score`: frecency for the tile
	* `url`: signals that the tile is enhanced. absent otherwise. value is empty, i.e. no urls are sent


## /v2/links/click

The `click` endpoint captures any click interaction with the tile. This includes `click`, `block`, `pin`, `unpin`, `sponsored`, and `sponsored_link`.

When the user interacts with the tile, an asynchronous ping is sent to Mozilla servers. This is to measure a click event. Since our business model is Cost per Click (CPC), this metric is vital.

Positive events and perhaps more importantly, negative events like `block` and `unpin` are also very important. It can tell us that certain tiles are not appropriate or that people do not like them.

Method: POST

Example Payload:

    {
      "click": 1,
      "tiles": [
        {
          "id": 8,
          "pin": true,
          "pos": 2,
          "score": 2000,
          "enhanced": 1
        },
        {
          "id": 12
        },
        ...
      ]
    }

Parameters:

* `click`/`block`/`pin`/`unpin`/`sponsored`/`sponsored_link`: Only one of these can happen in one payload. The value of this `action` is the index in `tiles` for which this action applies
* The rest of the parameters are the same as for `/v2/links/view`

