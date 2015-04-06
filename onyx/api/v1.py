import logging
from flask import (
    current_app,
    Blueprint,
    request,
    make_response,
    redirect,
    Response
)
from werkzeug.exceptions import BadRequest
from onyx.environment import Environment


links = Blueprint('v1_links', __name__, url_prefix='/v1/links')
env = Environment.instance()


@links.route('/fetch', methods=['POST'])
@env.statsd.timer('v1_links_fetch')
def fetch():
    """
    Given a locale, return locale-specific links if possible.
    """
    reject = False
    ip_addr = None
    ua = None
    locale = None
    directory_count = None

    try:
        ip_addr = request.remote_addr
        ua = request.headers.get('User-Agent')
        client_payload = request.get_json(force=True, cache=False, silent=False)

        if not client_payload:
            raise BadRequest()

        locale = client_payload.get('locale')
        directory_count = client_payload.get('directoryCount')

        if locale is None:
            env.log_dict(name="client_error", action="fetch_locale_missing", level=logging.WARN, message={
                "ip": ip_addr,
                "ua": ua,
                "ver": "1",
            })
            reject = True

        if directory_count is None:
            env.log_dict(name="client_error", action="fetch_dirCount_missing", level=logging.WARN, message={
                "ip": ip_addr,
                "ua": ua,
                "ver": "1",
            })
            reject = True

    except:
        env.log_dict(name="client_error", action="fetch_malformed_payload", level=logging.WARN, message={
            "ip": ip_addr,
            "ua": ua,
            "ver": "1",
        })
        reject = True

    if reject:
        env.statsd.incr("fetch_error")
        return Response('', content_type='application/json; charset=utf-8',
                        status=400)

    try:
        country = env.geoip_db.country(ip_addr).country.iso_code
    except:
        country = "ERROR"

    localized = current_app.config['LINKS_LOCALIZATIONS'].get("%s/%s" % (country, locale), {}).get('legacy')
    if localized is None:
        localized = env.config.LINKS_LOCALIZATIONS.get("STAR/%s" % locale, {}).get('legacy')

    if localized:
        # 303 hints to the client to always use GET for the redirect
        # ETag is handled by the directory link hosting server
        response = make_response(redirect(localized, code=303))
        env.log_dict(name="application", action="fetch_served", message={
            "ip": ip_addr,
            "ua": ua,
            "locale": locale,
            "dirCount": directory_count,
            "ver": "1",
        })
        env.statsd.incr("fetch_success")
    else:
        response = make_response(('', 204))
        env.log_dict(name="application", action="fetch_locale_unavailable", message={
            "ip": ip_addr,
            "ua": ua,
            "locale": locale,
            "dirCount": directory_count,
            "ver": "1",
        })
        env.statsd.incr("fetch_locale_unavailable")

    return response


def register_routes(app):
    app.register_blueprint(links)
