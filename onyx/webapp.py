from flask import Flask

def create_app(config_filename):
    # TODO: forward proxy headers
    app = Flask(__name__)
    if not config_filename:
        app.config.from_object('onyx.default_settings.DefaultConfig')
    else:
        #TODO: read config in a format of choice. JSON?
        pass
    return app

def setup_routes(app):
    import onyx.api.v1
    onyx.api.v1.register_routes(app)

    if app.config['DEBUG'] and app.config['ENVIRONMENT'] == 'dev':
        # TODO: set static routes
        pass
