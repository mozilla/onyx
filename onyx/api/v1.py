import json
from flask import (
    current_app,
    Blueprint,
    request,
    make_response,
    redirect,
    Response
)
import onyx
from heka_raven.raven_plugin import capture_stack

links = Blueprint('v1_links', __name__, url_prefix='/v1/links')


@links.route('/newtab', methods=['POST'])
# @onyx.hekalog.timer('newtab_serving')
@capture_stack
def newtab_serving():
    """
    Given a locale, return locale-specific links if possible.
    Set an identifier for a user if it isn't already set.
    """
    try:
        client_payload = request.get_json(cache=False)
        locale = client_payload['locale']
    except Exception:
        onyx.hekalog.incr('payload_error', logger='watchlist', severity=3)
        return Response('', content_type='application/json; charset=utf-8',
                        status=400)

    localized = current_app.config['LINKS_LOCALIZATIONS'].get(locale)

    response = None

    if localized:
        # 303 hints to the client to always use GET for the redirect
        # ETag is handled by the directory link hosting server
        response = make_response(redirect(localized, code=303))
        onyx.hekalog.heka(type='serving', logger='payload_served',
                          payload=json.dumps({
                              'ip': request.remote_addr,
                              'locale': locale
                          }))
    else:
        response = make_response(('', 204))

    return response


def register_routes(app):
    app.register_blueprint(links)
