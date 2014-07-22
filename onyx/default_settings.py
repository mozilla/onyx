from datetime import timedelta
from Crypto.Protocol.KDF import PBKDF2


class DefaultConfig(object):
    """
    Configuration suitable for use for development
    """
    DEBUG = True
    APPLICATION_ROOT = None
    JSONIFY_PRETTYPRINT_REGULAR = True

    STATIC_ENABLED_ENVS = {'dev', 'test'}
    ENVIRONMENT = 'dev'
    LINKS_LOCALIZATIONS = {
        'en-US': '/static/directoryLinks.json',
    }

    STATSD = {
            'host': 'localhost',
            'port': 8125,
    }

    LOG_PATH = None
    LOG_BACKUPS = 100
    LOG_MAX_BYTES = 1*1024*1024
