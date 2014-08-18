def setup_routes(app):
    import onyx.api.v1
    onyx.api.v1.register_routes(app)

    import onyx.api.v2
    onyx.api.v2.register_routes(app)
