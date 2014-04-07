from datetime import timedelta

class DefaultConfig(object):
    """
    Configuration suitable for use for development
    """
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_NAME = "onyx-session-dev"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SECRET_KEY = 'development-key-please-change-me'
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    APPLICATION_ROOT = None
    PREFERRED_URL_SCHEME = 'http'
    JSONIFY_PRETTYPRINT_REGULAR = True

    ENVIRONMENT = 'dev'
    LINKS_LOCATION = '/static/directoryLinks.json'
