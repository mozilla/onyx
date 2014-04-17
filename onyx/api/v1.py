from flask import current_app, Blueprint, request, redirect, jsonify

links = Blueprint('v1_links', __name__, url_prefix='/v1/links')

@links.route('/newtab/<locale>', methods=['POST'])
def newtab_serving(locale):
    """
    Given a locale, return locale-specific links if possible.
    """

    localized = current_app.config['LINKS_LOCALIZATIONS'].get(locale)

    if localized:
        # 303 hints to the client to always use GET for the redirect
        # ETag is handled by the directory link hosting server
        return redirect(localized, code=303)
    else:
        return '', 204

def register_routes(app):
    app.register_blueprint(links)
