def setup_routes(app):
    import onyx.api.v1
    onyx.api.v1.register_routes(app)

    import onyx.api.v2
    onyx.api.v2.register_routes(app)

    import onyx.api.v3
    onyx.api.v3.register_routes(app)

    import onyx.api.v4
    onyx.api.v4.register_routes(app)

    import onyx.api.heartbeat
    onyx.api.heartbeat.register_routes(app)
