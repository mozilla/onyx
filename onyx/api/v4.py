from flask import Blueprint
from onyx.environment import Environment
from onyx.api.v3 import handle_activity_stream_ping


links = Blueprint('v4_links', __name__, url_prefix='/v4/links')
env = Environment.instance()


@links.route('/activity-stream', methods=['POST'])
@env.statsd.timer('v4_links_activity_stream')
def activity_stream():
    """Log activity stream ping sent from Firefox on each session"""
    return handle_activity_stream_ping("activity_stream", "activity_stream")


def register_routes(app):
    app.register_blueprint(links)
