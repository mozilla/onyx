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
    ENVIRONMENT = 'dev'
    LINKS_LOCALIZATIONS = {
        'en-US': '/static/directoryLinks.json',
    }

    STATSD = {
            'host': 'localhost',
            'port': 8125,
    }

    LOG_HANDLERS = {
            'application': {
                'handler': logging.handlers.SysLogHandler,
                'level': logging.INFO,
                'params': {
                    'address': "/var/run/syslog",
                    'facility': logging.handlers.SysLogHandler.LOG_LOCAL0,
                    'socktype': socket.SOCK_DGRAM,
                }
            },
            'client_error': {
                'handler': logging.handlers.SysLogHandler,
                'level': logging.INFO,
                'params': {
                    'address': "/var/run/syslog",
                    'facility': logging.handlers.SysLogHandler.LOG_LOCAL1,
                    'socktype': socket.SOCK_DGRAM,
                }
            },
            'user_event': {
                'handler': logging.handlers.SysLogHandler,
                'format': '%(message)s',
                'level': logging.INFO,
                'params': {
                    'address': "/var/run/syslog",
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
