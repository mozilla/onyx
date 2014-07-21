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
import statsd
from onyx.utils import timed
from onyx.environment import Environment


counters = {
    'fetch_error': statsd.Counter('fetch_error'),
    'fetch_success': statsd.Counter('fetch_success'),
    'fetch_no_locale': statsd.Counter('fetch_no_locale'),
}

links = Blueprint('v1_links', __name__, url_prefix='/v1/links')
env = Environment.instance()

@timed('v1', 'newtab_serving')
@links.route('/newtab', methods=['POST'])
def newtab_serving():
    """
    Given a locale, return locale-specific links if possible.
    Set an identifier for a user if it isn't already set.
    """
    reject = False

    try:
        client_payload = request.get_json(cache=False)
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
        counters['fetch_error'] += 1
        return Response('', content_type='application/json; charset=utf-8',
                        status=400)

    localized = current_app.config['LINKS_LOCALIZATIONS'].get(locale)

    if localized:
        # 303 hints to the client to always use GET for the redirect
        # ETag is handled by the directory link hosting server
        response = make_response(redirect(localized, code=303))
        env.log(type="serving", logger="payload_served", message="{0} {1} {2}".format(
            request.remote_addr,
            locale,
            directory_count
        ))
        counters['fetch_success'] += 1
    else:
        counters['fetch_no_locale'] += 1
        response = make_response(('', 204))

    return response


def register_routes(app):
    app.register_blueprint(links)
