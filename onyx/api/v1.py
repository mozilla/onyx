import uuid
import json
from flask import current_app, Blueprint, request, make_response, redirect, jsonify, session
from onyx.encryption import encrypt, decrypt

links = Blueprint('v1_links', __name__, url_prefix='/v1/links')

@links.route('/newtab/<locale>', methods=['POST'])
def newtab_serving(locale):
    """
    Given a locale, return locale-specific links if possible.
    Set an identifier for a user if it isn't already set.
    """
    ciphertext = session.get('ciphertext')
    iv = session.get('iv')

    session_id = None
    try:
        if ciphertext and iv:
            data = json.loads(decrypt(ciphertext, iv))
            session_id = data['sid']
    except:
        return '', 400

    localized = current_app.config['LINKS_LOCALIZATIONS'].get(locale)

    response = None

    if localized:
        # 303 hints to the client to always use GET for the redirect
        # ETag is handled by the directory link hosting server
        response = make_response(redirect(localized, code=303))
    else:
        response = make_response(('', 204))

    # set cookie if need be
    if not session_id:
        data = {
            'sid': uuid.uuid4().hex
        }
        ciphertext, iv = encrypt(json.dumps(data))
        session['ciphertext'] = ciphertext
        session['iv'] = iv
        #TODO: save session id

    return response

def register_routes(app):
    app.register_blueprint(links)
