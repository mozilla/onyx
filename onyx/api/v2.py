import logging
from flask import (
    Blueprint,
    request,
    make_response,
    redirect,
    Response
)
from onyx.environment import Environment
import ujson


links = Blueprint('v2_links', __name__, url_prefix='/v2/links')
env = Environment.instance()


@env.statsd.timer('v2_links_fetch')
@links.route('/fetch', methods=['POST'])
def fetch():
    """
    Given a locale, return locale-specific links if possible.
    """
    ip_addr = None
    ua = None
    locale = None

    try:
        ip_addr = request.headers.get('X-Forwarded-For')
        if ip_addr is None:
            ip_addr = request.remote_addr

        ua = request.headers.get('User-Agent')
        raw_client_payload = request.get_data(cache=False)
        client_payload = ujson.decode(raw_client_payload)

        locale = client_payload['locale']

    except Exception:
        env.log_dict(name="client_error", action="fetch_malformed_payload", level=logging.WARN, message={
            "ip": ip_addr,
            "ua": ua,
            "locale": locale,
            "ver": "2",
        })
        env.statsd.incr("fetch_error")
        return Response('', content_type='application/json; charset=utf-8',
                        status=400)

    try:
        country = env.geoip_db.country(ip_addr).country.iso_code
    except:
        country = "ERROR"

    localized = env.config.LINKS_LOCALIZATIONS.get("%s/%s" % (country, locale))

    if localized:
        # 303 hints to the client to always use GET for the redirect
        # ETag is handled by the directory link hosting server
        response = make_response(redirect(localized, code=303))
        env.log_dict(name="application", action="fetch_served", message={
            "ip": ip_addr,
            "ua": ua,
            "locale": locale,
            "ver": "2",
        })
        env.statsd.incr("fetch_success")
    else:
        response = make_response(('', 204))
        env.log_dict(name="application", action="fetch_locale_unavailable", message={
            "ip": ip_addr,
            "ua": ua,
            "locale": locale,
            "ver": "2",
        })
        env.statsd.incr("fetch_locale_unavailable")

    return response


def handle_ping(ping_type):
    """
    A ping handler that just logs the data it receives for further processing
    in the backend
    """
    ip_addr = None
    ua = None
    locale = None

    try:
        client_payload_raw = request.get_data(cache=False)
        client_payload = ujson.decode(client_payload_raw)
        
        ip_addr = request.headers.get('X-Forwarded-For')
        if ip_addr == None:
            ip_addr = request.remote_addr
            
        ua = request.headers.get('User-Agent')
        client_payload["ua"] = ua
        client_payload["ip"] = ip_addr

    except Exception:
        env.log_dict(name="client_error", action="{0}_malformed_payload".format(ping_type), level=logging.WARN, message={
            "ip": ip_addr,
            "ua": ua,
            "locale": locale,
            "ver": "2",
        })

        env.statsd.incr("{0}".format(ping_type, "_error"))
        return Response('', content_type='application/json; charset=utf-8',
                        status=400)

    env.log_dict(name="user_event", message=client_payload)

    return Response('', content_type='application/json; charset=utf-8',
                    status=200)


@env.statsd.timer('v2_links_view')
@links.route('/view', methods=['POST'])
def view():
    """
    Log impression ping sent from Firefox on each newtab open event
    """
    return handle_ping("view")


@env.statsd.timer('v2_links_click')
@links.route('/click', methods=['POST'])
def click():
    """
    Log tile ping sent from Firefox on each tile action
    """
    return handle_ping("click")


def register_routes(app):
    app.register_blueprint(links)

