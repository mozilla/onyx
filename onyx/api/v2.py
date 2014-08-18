import json
import logging
from datetime import datetime
import calendar
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


links = Blueprint('v2_links', __name__, url_prefix='/v2/links')
env = Environment.instance()

@env.statsd.timer('v2_links_fetch')
@links.route('/fetch', methods=['POST'])
def fetch():
    """
    Given a locale, return locale-specific links if possible.
    """
    reject = False

    try:
        client_payload = request.get_json(force=True, cache=False, silent=False)

        if not client_payload:
            raise BadRequest()

        locale = client_payload.get('locale')

        if locale is None:
            env.log(logger="fetch", type="client_error", message="locale_missing", level=logging.WARN)
            reject = True

    except BadRequest:
        env.log(logger="fetch", type="client_error", message="malformed_payload", level=logging.WARN)
        reject = True
    except Exception:
        env.log(logger="fetch", type="client_error", message="malformed_payload", level=logging.WARN)
        reject = True

    if reject:
        env.statsd.incr("fetch_error")
        return Response('', content_type='application/json; charset=utf-8',
                        status=400)

    localized = current_app.config['LINKS_LOCALIZATIONS'].get(locale)

    if localized:
        # 303 hints to the client to always use GET for the redirect
        # ETag is handled by the directory link hosting server
        response = make_response(redirect(localized, code=303))
        env.log(logger="fetch", type="served", message=" ".join([
            str(request.remote_addr),
            locale
        ]))
        env.statsd.incr("fetch_success")
    else:
        response = make_response(('', 204))
        env.log(logger="fetch", type="locale_unavailable", message=" ".join([
            str(request.remote_addr),
            locale
        ]))
        env.statsd.incr("fetch_locale_unavailable")

    return response

def handle_ping(ping_type):

    reject = False

    try:
        client_payload = request.get_json(force=True, cache=False, silent=False)

        if not client_payload and type(client_payload) == dict:
            raise BadRequest()
    except BadRequest:
        env.log(logger=ping_type, type="client_error", message="malformed_payload", level=logging.WARN)
        reject = True
    except Exception:
        env.log(logger=ping_type, type="client_error", message="malformed_payload", level=logging.WARN)
        reject = True

    if reject:
        env.statsd.incr("{0}".format(ping_type, "_error"))
        return Response('', content_type='application/json; charset=utf-8',
                        status=400)

    now = datetime.utcnow()
    date_str = now.date().isoformat()
    timestamp = calendar.timegm(now.timetuple())

    client_payload["date"] = date_str
    client_payload["timestamp"] = timestamp

    env.log(logger=ping_type, type="payload", message=json.dumps(client_payload))

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

