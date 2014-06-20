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

    HEKA = {
        'logger': 'onyx-{0}'.format(ENVIRONMENT),
        'severity': 4,
        'stream': {
            'class': 'heka.streams.StdLibLoggingStream',
            'logger_name': 'onyx-{0}'.format(ENVIRONMENT),
        },
        'encoder': 'heka.encoders.StdlibPayloadEncoder',
    }
