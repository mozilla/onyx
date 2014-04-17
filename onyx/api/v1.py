from flask import current_app, Blueprint, request, redirect, jsonify

links = Blueprint('v1_links', __name__, url_prefix='/v1/links')

@links.route('/newtab/impression', methods=['POST'])
def newtab_impression():
    """
    Collect stats about newtab page impressions
    """
    return '', 201

@links.route('/newtab', methods=['POST'])
def newtab_serving():
    # redirecting 303 will hint to the client to change HTTP verb to GET
    return redirect(current_app.config['LINKS_LOCATION'], code=303)

def register_routes(app):
    app.register_blueprint(links)
