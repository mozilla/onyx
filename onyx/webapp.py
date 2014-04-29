from flask import Flask, current_app
from flask_sslify import SSLify

def create_app(config_filename):
    # TODO: forward proxy headers
    app = Flask(__name__)
    SSLify(app, subdomains=True, permanent=True)
    if not config_filename:
        app.config.from_object('onyx.default_settings.DefaultConfig')
    else:
        app.config.from_object(config_filename)

    if app.config['ENVIRONMENT'] not in app.config['STATIC_ENABLED_ENVS']:
        app.config['STATIC_FOLDER'] = None

    return app

def setup_routes(app):
    try:
        import onyx.api.v1
        onyx.api.v1.register_routes(app)
    except Exception, e:
        current_app.hekalog.exception(e)
