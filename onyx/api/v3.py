import random
import ujson

from flask import (
    Blueprint,
    request,
    make_response,
    Response,
    redirect
)
from onyx.environment import Environment
from onyx.api.v2 import handle_ping


links = Blueprint('v3_links', __name__, url_prefix='/v3/links')
env = Environment.instance()
channels_valid = {'esr', 'release', 'beta', 'aurora', 'nightly', 'android', 'hello'}
channels_prerelease = {'beta', 'aurora', 'nightly'}
channels_release = {'esr', 'release'}


@links.route('/fetch/<locale>/<channel>', methods=['GET'])
@env.statsd.timer('v3_links_fetch')
def fetch(locale=None, channel=None):
    """
    Given a locale, return locale-specific links if possible.
    """
    ip_addrs = None
    ip_addr = None
    ua = None

    ip_addrs = request.headers.get('X-Forwarded-For')
    if ip_addrs is None:
        ip_addrs = request.remote_addr

    if ip_addrs is not None:
        ip_addr = ip_addrs.split(',')[0]

    ua = request.headers.get('User-Agent')

    try:
        country = env.geoip_db.country(ip_addr).country.iso_code
    except:
        country = 'STAR'

    selected_channel = 'desktop'  # default will be desktop, even in case an unrecognized channel is requested
    if channel in channels_valid:
        if channel in channels_prerelease:
            selected_channel = 'desktop-prerelease'
        elif channel in channels_release:
            selected_channel = 'desktop'
        else:
            selected_channel = channel

    localized = None

    try:
        localized = env.config.LINKS_LOCALIZATIONS[selected_channel].get("%s/%s" % (country, locale), {}).get('ag')
    except KeyError:
        # fail loudly if LINKS_LOCALIZATIONS doesn't have the desired channel. Will return with a 500 error
        env.log_dict(name="application", action="fetch_channel_missing", message={
            "ip": ip_addrs,
            "ua": ua,
            "locale": locale,
            "channel": selected_channel,
            "ver": "3",
        })
        env.statsd.incr("fetch_error")
        return Response('', content_type='application/json; charset=utf-8',
                        status=500)

        # Note: localized could still be None if there is no country-specific tiles
    if localized is None:
        localized = env.config.LINKS_LOCALIZATIONS[selected_channel].get("STAR/%s" % locale, {}).get('ag')

    if isinstance(localized, list):
        localized = random.choice(localized) if localized else None

    if localized is not None:
        # 303 hints to the client to always use GET for the redirect
        # ETag is handled by the directory link hosting server
        resp = redirect(localized, code=303)
        resp.data = ''
        response = make_response(resp)
        env.log_dict(name="application", action="fetch_served", message={
            "ip": ip_addrs,
            "ua": ua,
            "locale": locale,
            "channel": channel,
            "ver": "3",
        })
        env.statsd.incr("fetch_success")
    else:
        response = make_response(('', 204))
        env.log_dict(name="application", action="fetch_locale_unavailable", message={
            "ip": ip_addrs,
            "ua": ua,
            "locale": locale,
            "channel": channel,
            "ver": "3",
        })
        env.statsd.incr("fetch_locale_unavailable")

    return response


@links.route('/view', methods=['POST'])
@env.statsd.timer('v3_links_view')
def view():
    """
    Log impression ping sent from Firefox on each newtab open event
    """
    return handle_ping("view", api_version="3")


@links.route('/click', methods=['POST'])
@env.statsd.timer('v3_links_click')
def click():
    """
    Log tile ping sent from Firefox on each tile action
    """
    return handle_ping("click", api_version="3")


def handle_activity_stream_ping(ping_type, log_name):
    ip_addr = None
    ua = None
    action = None

    try:
        client_payload_raw = request.get_data(cache=False)
        client_payload = ujson.decode(client_payload_raw)
        action = client_payload["action"]  # treat it as malformed payload if "action" is missing

        ip_addr = request.headers.get('X-Forwarded-For')
        if ip_addr is None:
            ip_addr = request.remote_addr

        ua = request.headers.get('User-Agent')
        client_payload["ua"] = ua
        client_payload["ip"] = ip_addr
    except Exception:
        env.log_dict(name="client_error", action="{0}_malformed_payload".format(ping_type), message={
            "ip": ip_addr,
            "ua": ua,
            "ver": 3,
        })

        env.statsd.incr("{0}_error".format(ping_type))
        return Response('', content_type='application/json; charset=utf-8',
                        status=400)

    env.log_dict(name=log_name, action=action, message=client_payload)

    env.statsd.incr("{0}".format(ping_type))
    return Response('', content_type='application/json; charset=utf-8',
                    status=200)


@links.route('/activity-stream', methods=['POST'])
@env.statsd.timer('v3_links_activity_stream')
def activity_stream():
    """Log activity stream ping sent from Firefox on each session"""
    return handle_activity_stream_ping("activity_stream", "application")


def handle_ping_centre_ping(ping_type, log_name):
    ip_addr = None
    ua = None

    try:
        client_payload_raw = request.get_data(cache=False)
        client_payload = ujson.decode(client_payload_raw)
        assert 'topic' in client_payload  # treat it as malformed payload if "topic" is missing
        action = client_payload.get("action", "ping_centre")

        ip_addr = request.headers.get('X-Forwarded-For')
        if ip_addr is None:
            ip_addr = request.remote_addr

        ua = request.headers.get('User-Agent')
        client_payload["ua"] = ua
        client_payload["ip"] = ip_addr
    except Exception:
        env.log_dict(name="client_error", action="{0}_malformed_payload".format(ping_type), message={
            "ip": ip_addr,
            "ua": ua,
            "ver": 3,
        })

        env.statsd.incr("{0}_error".format(ping_type))
        return Response('', content_type='application/json; charset=utf-8',
                        status=400)

    env.log_dict(name=log_name, action=action, message=client_payload)

    env.statsd.incr("{0}".format(ping_type))
    return Response('', content_type='application/json; charset=utf-8',
                    status=200)


@links.route('/ping-centre', methods=['POST'])
@env.statsd.timer('v3_links_ping_centre')
def ping_centre():
    """Log ping-centre ping sent from Firefox users on each session"""
    return handle_ping_centre_ping("ping_centre", "ping_centre")


def register_routes(app):
    app.register_blueprint(links)
