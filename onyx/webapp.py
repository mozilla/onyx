import onyx

def setup_routes(app):
    try:
        import onyx.api.v1
        onyx.api.v1.register_routes(app)
    except Exception, e:
        onyx.hekalog.exception('route_error')
