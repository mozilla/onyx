#!/usr/bin/env python

from optparse import OptionParser
import grequests
import requests
requests.packages.urllib3.disable_warnings()


def main():
    # get argument
    parser = OptionParser(usage='Usage: %prog [OPTIONS]')
    parser.set_defaults(
        cdn='https://tiles.cdn.mozilla.net',
        channels=[],
        geoip_blocks='/usr/share/GeoIP/GeoIP2-Country-Blocks-IPv4.csv',
        geoip_locations='/usr/share/GeoIP/GeoIP2-Country-Locations-en.csv',
        onyx='https://tiles.services.mozilla.com',
        quiet=False,
        tile_index_key='tile_index_v3.json',
        verbose=False,
    )
    parser.add_option(
        '-b', '--geoip-blocks',
        dest='geoip_blocks',
        help='Path to GeoIP2-Country-Blocks-IPv4.csv',
        metavar='CSV',
    )
    parser.add_option(
        '-c', '--cdn-url',
        dest='cdn',
        help='URL of the CDN or s3 bucket. Of the form "<scheme>://<fqdn>".'
        ' Trailing "/" not allowed.',
        metavar='URL',
    )
    parser.add_option(
        '--channels',
        action='append',
        dest='channels',
        help='Path to GeoIP2-Country-Locations-en.csv',
        metavar='CSV',
    )
    parser.add_option(
        '-l', '--geoip-locations',
        dest='geoip_locations',
        help='Path to GeoIP2-Country-Locations-en.csv',
        metavar='CSV',
    )
    parser.add_option(
        '-o', '--onyx-url',
        dest='onyx',
        help='URL of the Onyx server. Of the form "<scheme>://<fqdn>".'
        ' Trailing "/" not allowed.',
        metavar='URL',
    )
    parser.add_option(
        '-q', '--quiet',
        action='store_true',
        dest='quiet',
        help="Don't report NOTICE",
    )
    parser.add_option(
        '-t', '--tile-index-key',
        dest='tile_index_key',
        help='suffix of tile index file',
        metavar='SUFFIX',
    )
    parser.add_option(
        '-v', '--verbose',
        action='store_true',
        dest='verbose',
        help='Report SUCCESS',
    )
    options, args = parser.parse_args()

    cdn = options.cdn
    onyx = options.onyx
    errors = 0

    if not options.channels:
        options.channels = ['desktop']

    if len(args) > 0:
        parser.parse_args(['-h'])

    if not options.quiet:
        print(
            'NOTICE: validating %s/<channel>_%s for channel in %s' %
            (cdn, options.tile_index_key, options.channels)
        )
        print('NOTICE: downloading indexes')

    indexes = [
        (channel, index)
        for channel in options.channels
        for index in grequests.map([
            grequests.get(
                '%s/%s_%s' %
                (cdn, channel, options.tile_index_key),
                allow_redirects=False,
            )
        ])
    ]

    if not options.quiet:
        print('NOTICE: downloaded %s indexes' % len(indexes))
        print('NOTICE: calculating urls')

    countries = {}
    for channel, index in indexes:
        try:
            if index.status_code != 200:
                print('ERROR: %s %s' % (index.url, index.status_code))
                errors += 1
            elif options.verbose:
                print('SUCCESS: %s %s' % (index.url, index.status_code))

            for key, value in index.json().iteritems():
                if '/' in key:
                    country, locale = key.split('/', 1)
                    if country not in countries:
                        countries[country] = {}

                    # channel ignorant urls
                    if channel == 'desktop':
                        # v2 urls
                        url = onyx + '/v2/links/fetch/' + locale
                        countries[country][url] = value['legacy']

                    # v3 urls
                    url = (
                        '%s/v3/links/fetch/%s/%s' %
                        (onyx, locale, channel)
                    )
                    countries[country][url] = value['ag']
        except Exception as e:
            print('ERROR: %s' % e)
            errors += 1

    if not options.quiet:
        print('NOTICE: calculated %s urls' % sum(len(urls) for urls in countries.values()))
        print('NOTICE: calculating country geoname ids')

    ips = {}
    geonames = {}

    # convert iso_codes to geonames
    unmapped = set(countries.keys())

    if 'STAR' in unmapped:
        unmapped.remove('STAR')
        unmapped.add('')

    with open(options.geoip_locations) as pointer:
        for line in pointer:
            try:
                geoname, _, _, _, iso_code, _ = line.split(',', 5)
            except Exception:
                continue
            if iso_code in unmapped:
                geonames[geoname] = iso_code
                unmapped.remove(iso_code)
            elif not unmapped:
                break

    if not options.quiet:
        print('NOTICE: calculated %s geoname ids' % len(geonames))
        print('NOTICE: calculating country ips')

    # get ips from geonames
    unmapped = set(geonames.keys())

    with open(options.geoip_blocks) as pointer:
        for line in pointer:
            try:
                subnet, geoname, _ = line.split(',', 2)
                ip = subnet.split('/', 1)[0]
            except Exception:
                continue
            if geoname in unmapped:
                ips[geonames[geoname]] = ip
                unmapped.remove(geoname)
            elif not unmapped:
                break

    if '' in ips:
        ips['STAR'] = ips['']
        del ips['']

    if not options.quiet:
        print('NOTICE: calculated %s country ips' % len(ips))
        print('NOTICE: requesting urls')

    # request urls
    results_by_country = {
        country: grequests.map(
            grequests.get(
                url,
                allow_redirects=False,
                headers={'X-Geoip-Override': ips[country]}
            )
            for url in urls.keys()
        )
        for country, urls in countries.iteritems()
    }

    if not options.quiet:
        print('NOTICE: requested %s urls' % len(results_by_country))
        print('NOTICE: validating responses')

    # validate results
    error = 0
    success = 0
    for country, results in results_by_country.iteritems():
        for result in results:
            if result.status_code != 303:
                print(
                    'ERROR: %s (%s) %s' %
                    (
                        result.url,
                        country,
                        result.status_code,
                    )
                )
                error += 1
            elif result.headers['location'] not in countries[country][result.url]:
                print(
                    'ERROR: %s (%s) %s != %s' %
                    (
                        result.url,
                        country,
                        result.headers['location'],
                        countries[country][result.url]
                    )
                )
                error += 1
            elif options.verbose:
                print(
                    'SUCCESS: %s (%s) %s' %
                    (
                        result.url,
                        country,
                        result.status_code,
                    )
                )
                success += 1
            else:
                success += 1

    if not options.quiet:
        print('NOTICE: validated %s responses' % (success + error))
        print('NOTICE: %s valid responses' % success)
        print('NOTICE: %s invalid responses' % error)

    errors += error

    if errors:
        exit(1)


if __name__ == '__main__':
    main()
