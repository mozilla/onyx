import ujson

from flask import (
    Blueprint,
    request,
    Response,
)

from onyx.environment import Environment
from onyx.api.v3 import handle_activity_stream_ping


links = Blueprint('v4_links', __name__, url_prefix='/v4/links')
env = Environment.instance()


@links.route('/activity-stream', methods=['POST'])
@env.statsd.timer('v4_links_activity_stream')
def activity_stream():
    """Log activity stream ping sent from Firefox on each session"""
    return handle_activity_stream_ping("activity_stream", "activity_stream")


@links.route('/activity-stream/csp', methods=['POST'])
@env.statsd.timer('v4_links_activity_stream_csp')
def activity_stream_csp():
    """Log activity stream CSP report sent from Firefox on CSP violations"""
    ip_addr = None
    ua = None
    action = None

    try:
        client_payload_raw = request.get_data(cache=False)
        client_payload = ujson.decode(client_payload_raw)
        action = "activity_stream_csp"
        # treat it as malformed payload if "csp-report" is missing
        # see https://developers.google.com/web/fundamentals/security/csp/#reporting
        client_payload = client_payload["csp-report"]
        client_payload["action"] = action

        ip_addr = request.headers.get('X-Forwarded-For')
        if ip_addr is None:
            ip_addr = request.remote_addr

        ua = request.headers.get('User-Agent')
        client_payload["ua"] = ua
        client_payload["ip"] = ip_addr
    except Exception:
        env.log_dict(name="client_error", action="activity_stream_csp_malformed_payload", message={
            "ip": ip_addr,
            "ua": ua,
            "ver": 3,
        })

        env.statsd.incr("activity_stream_csp_error")
        return Response('', content_type='application/json; charset=utf-8', status=400)

    env.log_dict(name="activity_stream", action=action, message=client_payload)

    env.statsd.incr("activiyt_stream_csp")
    return Response('', content_type='application/json; charset=utf-8', status=200)


def register_routes(app):
    app.register_blueprint(links)
