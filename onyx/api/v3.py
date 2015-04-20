import logging
from flask import (
    Blueprint,
    request,
    make_response,
    redirect,
    Response
)
from onyx.environment import Environment
from onyx.api.v2 import handle_ping


links = Blueprint('v3_links', __name__, url_prefix='/v3/links')
env = Environment.instance()


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
        country = "STAR"

    localized = env.config.LINKS_LOCALIZATIONS.get("%s/%s" % (country, locale), {}).get('ag')
    if localized is None:
        localized = env.config.LINKS_LOCALIZATIONS.get("STAR/%s" % locale, {}).get('ag')

    if localized is not None:
        # 303 hints to the client to always use GET for the redirect
        # ETag is handled by the directory link hosting server
        response = make_response(redirect(localized, code=303))
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


def register_routes(app):
    app.register_blueprint(links)
