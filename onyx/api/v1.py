from flask import current_app, Blueprint, request, redirect, jsonify

links = Blueprint('v1_links', __name__, url_prefix='/v1/links')
clicks = Blueprint('v1_clicks', __name__, url_prefix='/v1/clicks')

@clicks.route('/newtab', methods=['POST'])
def newtab_click():
    """
    Collect stats about clicks on the newtab page
    """
    return '', 201

@links.route('/newtab', methods=['POST'])
def newtab_serving():
    # redirecting 303 will hint to the client to change HTTP verb to GET
    return redirect(current_app.config['LINKS_LOCATION'], code=303)

def register_routes(app):
    app.register_blueprint(links)
    app.register_blueprint(clicks)
