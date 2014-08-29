#!/bin/sh
#
# This script will download the tile index file out of s3 and dump it into the onyx data directory
# It is meant to be run periodically by cron (every 15 minutes)
#
# TODO: make bucket name configurable through puppet (see onyx.default_settings.TILE_INDEX*)

wget -O /var/data/onyx/tile_index.json onyx_data_bucket.s3.amazon.com/tile_index.json