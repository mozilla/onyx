import json
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
from onyx.utils import timed
from onyx.environment import Environment


links = Blueprint('v1_links', __name__, url_prefix='/v1/links')
env = Environment.instance()

@env.statsd.timer('v1_links_fetch')
@links.route('/fetch', methods=['POST'])
def fetch():
    """
    Given a locale, return locale-specific links if possible.
    Set an identifier for a user if it isn't already set.
    """
    reject = False

    try:
        client_payload = request.get_json(cache=False, silent=False)

        if not client_payload:
            raise BadRequest()

        locale = client_payload.get('locale')
        directory_count = client_payload.get('directoryCount')

        if locale is None:
            env.log(logger="fetch", type="client_error", message="locale_missing", level=logging.WARN)
            reject = True

        if directory_count is None:
            env.log(logger="fetch", type="client_error", message="directory_count_missing", level=logging.WARN)
            reject = True

    except BadRequest:
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
            locale,
            str(directory_count)
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


def register_routes(app):
    app.register_blueprint(links)
