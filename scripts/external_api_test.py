#!/usr/bin/env python

from optparse import OptionParser
import traceback
import grequests
import requests
requests.packages.urllib3.disable_warnings()


def main():
    # get argument
    parser = OptionParser(
        usage='Usage: %prog [<ONYX_URL> [<CDN_URL>]]'
        '\n\nArguments:'
        '\n  ONYX_URL   Of the format "<scheme>://<fqdn>".'
        ' Trailing "/" not allowed.'
        '\n  CDN_URL    Of the format "<scheme>://<fqdn>".'
        ' Trailing "/" not allowed.'
        '\n\nExamples:'
        '\n  %prog https://tiles.services.mozilla.com https://tiles.cdn.mozilla.net'
    )
    parser.set_defaults(verbose=False)
    parser.add_option(
        '-v', '--verbose',
        action='store_true',
        dest='verbose',
        help='Report SUCCESS as well as ERROR/WARNING',
    )
    options, args = parser.parse_args()

    cdn = 'https://tiles.cdn.mozilla.net'
    errors = 0
    onyx = 'https://tiles.services.mozilla.com'

    if len(args) == 1:
        onyx = args.pop()
    elif len(args) == 2:
        onyx, cdn = args
    elif len(args) > 2:
        parser.parse_args(['-h'])

    channel_mapping = {
        'desktop': ['esr', 'release'],
        'desktop-prerelease': ['beta', 'aurora', 'nightly'],
        'android': ['android'],
        'hello': ['hello']
    }

    for channel_name, release_names in channel_mapping.iteritems():
        try:
            # get tile index
            r = requests.get(
                '%s/%s_tile_index_v3.json' %
                (cdn, channel_name),
                allow_redirects=False
            )

            # validate index response
            if r.status_code != 200:
                raise Exception('ERROR: %s %s' % (r.url, r.status_code))
            elif options.verbose:
                print('SUCCESS: %s %s' % (r.url, r.status_code))

            # extract list of test urls from index
            urls = {}
            for key, value in r.json().iteritems():
                if '/' in key:
                    locale = key.split('/', 1).pop()

                    # v2 urls, only for desktop
                    if channel_name == 'desktop':
                        url = onyx + '/v2/links/fetch/' + locale
                        if url not in urls:
                            urls[url] = set()
                        urls[url].add(value['legacy'])

                    # v3 urls
                    for release in release_names:
                        url = (
                            '%s/v3/links/fetch/%s/%s' %
                            (onyx, locale, release)
                        )
                        if url not in urls:
                            urls[url] = set()
                        urls[url].add(value['ag'])

            # request urls
            results = grequests.imap(
                (
                    grequests.get(url, allow_redirects=False)
                    for url in sorted(urls.keys())),
                size=10)

            # validate results
            for r in results:
                if r.status_code != 303:
                    print('ERROR: %s %s' % (r.url, r.status_code))
                    errors += 1
                elif r.headers['location'] not in urls[r.url]:
                    print(
                        'ERROR: %s %s != %s' %
                        (r.url, r.headers['location'], ' '.join(sorted(list(urls[r.url]))))
                    )
                    errors += 1
                elif options.verbose:
                    print('SUCCESS: %s %s' % (r.url, r.status_code))
        except:
            print traceback.format_exc()
            errors += 1

    if errors > 0:
        print('%s ERRORS found' % errors)
        exit(1)


if __name__ == '__main__':
    main()
