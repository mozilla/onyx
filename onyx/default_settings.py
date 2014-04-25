from datetime import timedelta
from Crypto.Protocol.KDF import PBKDF2

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

    STATIC_ENABLED_ENVS = set(['dev', 'test'])
    ENVIRONMENT = 'dev'
    LINKS_LOCALIZATIONS = {
            'en-US': '/static/directoryLinks.json',
    }
    SESSION_MAX_AGE = 30
    ENCRYPTION = {
            'AES_KEY': PBKDF2(password='development-key-some-password', salt='development-salt-some-random-salt', dkLen=32, count=10000)
    }
