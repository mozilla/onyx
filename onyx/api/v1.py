from flask import current_app, Blueprint, request, redirect, jsonify

clicks = Blueprint('v1_clicks', __name__, url_prefix='/v1/clicks')

@clicks.route('/newtab', methods=['POST'])
def newtab_click():
    """
    Collect stats about clicks on the newtab page
    """
    return '', 201

links = Blueprint('v1_links', __name__, url_prefix='/v1/links')
@links.route('/newtab/impression', methods=['POST'])
def newtab_impression():
    """
    Collect stats about newtab page impressions
    """
    return '', 201

@links.route('/newtab', methods=['GET'])
def newtab_serving():
    return redirect(current_app.config['LINKS_LOCATION'])

def register_routes(app):
    app.register_blueprint(links)
    app.register_blueprint(clicks)
