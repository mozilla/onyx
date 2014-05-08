from heka_raven.raven_plugin import capture_stack


@capture_stack
def setup_routes(app):
    import onyx.api.v1
    onyx.api.v1.register_routes(app)
