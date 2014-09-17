#!/usr/bin/env python
import sys
import os
import argparse
import urllib2
import logging
from datetime import datetime


def main():
    desc = """
    This script will download the tile index file out of an arbitrary url and
    dump it into the onyx data directory.
    It is meant to be run periodically by cron (every 15 minutes).

    The insertion into the data directory is guaranteed to be atomic, and will
    only complete upon successful download.
    """

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('url', metavar='TILE_INDEX_URL', type=str,
                       help='the location of the tile index to download')
    parser.add_argument('dest', metavar='DEST', type=str,
                       help='the filepath to save the file at')
    parser.add_argument('--temp-dir', dest='temp_dir', default='/tmp', type=str,
                       help='specify temp storage before moving to destination')
    args = parser.parse_args()

    logging.info('downloading url:{0}'.format(args.url))
    try:
        data = urllib2.urlopen(args.url)

        if data.getcode() == 200:
            fname = 'tile-{0}.json'.format(datetime.utcnow().isoformat().replace(':', '-'))
            fpath = os.path.join(args.temp_dir, fname)
            with open(fpath, 'w') as f:
                logging.info('writing to path:{0}'.format(fpath))
                f.write(data.read())

            logging.info('moving src:{0} to dest:{1}'.format(fpath, args.dest))
            os.rename(fpath, args.dest)
    except Exception, e:
        logging.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s\t%(levelname)s\t%(message)s', level=logging.INFO)
    main()
