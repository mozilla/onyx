from datetime import timedelta
from Crypto.Protocol.KDF import PBKDF2


class DefaultConfig(object):
    """
    Configuration suitable for use for development
    """
    DEBUG = True
    TESTING = False
    APPLICATION_ROOT = None
    PREFERRED_URL_SCHEME = 'http'
    JSONIFY_PRETTYPRINT_REGULAR = True

    STATIC_ENABLED_ENVS = {'dev', 'test'}
    ENVIRONMENT = 'dev'
    LINKS_LOCALIZATIONS = {
        'en-US': '/static/directoryLinks.json',
    }

    STATSD = {
            'host': 'localhost',
            'port': 8125,
            'sample_rate': 1,
            'disabled': False
    }
