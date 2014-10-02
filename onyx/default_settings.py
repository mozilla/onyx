import os
import sys
import logging
import logging.handlers
import socket


class DefaultConfig(object):
    """
    Configuration suitable for use for development
    """
    DEBUG = True
    APPLICATION_ROOT = None
    JSONIFY_PRETTYPRINT_REGULAR = True

    STATIC_ENABLED_ENVS = {'dev', 'test'}

    TILE_INDEX_FILE = "tile_index.json"
    TILE_INDEX_DIR = "/var/data/onyx/"

    ENVIRONMENT = 'dev'
    LINKS_LOCALIZATIONS = {}

    GEO_DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/GeoLite2-Country.mmdb")

    STATSD = {
        'host': 'localhost',
        'port': 8125,
    }

    LOG_HANDLERS = {
        'application': {
            'handler': logging.handlers.SysLogHandler,
            'level': logging.INFO,
            'params': {
                'address': ('localhost', 514),
                'facility': logging.handlers.SysLogHandler.LOG_LOCAL0,
                'socktype': socket.SOCK_DGRAM,
            }
        },
        'client_error': {
            'handler': logging.handlers.SysLogHandler,
            'level': logging.INFO,
            'params': {
                'address': ('localhost', 514),
                'facility': logging.handlers.SysLogHandler.LOG_LOCAL1,
                'socktype': socket.SOCK_DGRAM,
            }
        },
        'user_event': {
            'handler': logging.handlers.SysLogHandler,
            'format': '%(message)s',
            'level': logging.INFO,
            'params': {
                'address': ('localhost', 514),
                'facility': logging.handlers.SysLogHandler.LOG_LOCAL2,
                'socktype': socket.SOCK_DGRAM,
            }
        },
        'console': {
            'handler': logging.StreamHandler,
            'level': logging.DEBUG,
            'params': {
                'stream': sys.stdout
            }
        },
    }
