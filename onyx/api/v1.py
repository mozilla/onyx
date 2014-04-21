import uuid
from flask import current_app, Blueprint, request, make_response, redirect, jsonify, session

links = Blueprint('v1_links', __name__, url_prefix='/v1/links')

@links.route('/newtab/<locale>', methods=['POST'])
def newtab_serving(locale):
    """
    Given a locale, return locale-specific links if possible.
    Set an identifier for a user if it isn't already set.
    """
    user_id = session.get('uid')
    localized = current_app.config['LINKS_LOCALIZATIONS'].get(locale)

    response = None

    if localized:
        # 303 hints to the client to always use GET for the redirect
        # ETag is handled by the directory link hosting server
        response = make_response(redirect(localized, code=303))
    else:
        response = make_response(('', 204))

    # set cookie if need be
    if not user_id:
        session['uid'] = uuid.uuid4().hex
        #TODO: save cookie

    return response

def register_routes(app):
    app.register_blueprint(links)
