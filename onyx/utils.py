from onyx.webapp import create_app, setup_routes

def environment_manager_create(config):
    app = create_app(config)
    setup_routes(app)
    return app
