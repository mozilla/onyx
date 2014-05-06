import uuid
import json
from datetime import datetime, timedelta
import calendar
from flask import current_app, Blueprint, request, make_response, redirect, jsonify, session, Response
import onyx
from onyx.encryption import encrypt, decrypt
from heka_raven.raven_plugin import capture_stack

links = Blueprint('v1_links', __name__, url_prefix='/v1/links')

@links.route('/newtab', methods=['POST'])
@onyx.hekalog.timer('newtab_serving')
@capture_stack
def newtab_serving():
    """
    Given a locale, return locale-specific links if possible.
    Set an identifier for a user if it isn't already set.
    """
    ciphertext = session.get('ciphertext')
    iv = session.get('iv')

    try:
        client_payload = request.get_json(cache=False)
        locale = client_payload['locale']
    except Exception, e:
        onyx.hekalog.incr('payload_error', logger='watchlist', severity=3)
        return Response('', content_type='application/json; charset=utf-8', status=400)

    session_id = None
    created = None
    try:
        if ciphertext and iv:
            data = json.loads(decrypt(ciphertext, iv))
            session_id = data['sid']
            created = datetime.fromtimestamp(data['created'])
    except Exception, e:
        onyx.hekalog.incr('cookie_error', logger='watchlist', severity=3)
        return Response('', content_type='application/json; charset=utf-8', status=400)

    localized = current_app.config['LINKS_LOCALIZATIONS'].get(locale)

    response = None

    if localized:
        # 303 hints to the client to always use GET for the redirect
        # ETag is handled by the directory link hosting server
        response = make_response(redirect(localized, code=303))
        onyx.hekalog.heka(type='serving', logger='payload_served', payload=json.dumps({'ip': request.remote_addr, 'locale': locale}))
    else:
        response = make_response(('', 204))

    # (re)set cookie if need be
    if not session_id or (datetime.utcnow() - created > timedelta(days=current_app.config['SESSION_MAX_AGE'])):
        """
        Generate a new session ciphertext and initialization vector
        Set it in the current request session
        """
        new_data = {
            'sid': uuid.uuid4().hex,
            'created': calendar.timegm(datetime.utcnow().timetuple())
        }
        ciphertext, iv = encrypt(json.dumps(new_data))
        session['ciphertext'] = ciphertext
        session['iv'] = iv

        onyx.hekalog.heka(type='serving', logger='session_change', payload=json.dumps({'ip': request.remote_addr, 'old': session_id, 'new': new_data['sid']}))

    return response

def register_routes(app):
    app.register_blueprint(links)
