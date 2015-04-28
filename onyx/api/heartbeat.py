from flask import (
    Blueprint,
)
from onyx.environment import Environment


hb = Blueprint('heartbeat', __name__, url_prefix='/')
env = Environment.instance()


@hb.route('__heartbeat__', methods=['GET'])
def report():
    """
    Return OK to say the server works OK
    """
    return ''

def register_routes(app):
    app.register_blueprint(hb)
