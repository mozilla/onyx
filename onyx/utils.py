import sys
import multiprocessing
import logging
import os
from os.path import abspath, dirname
from functools import wraps
from datetime import datetime

from flask.ext.script import Command, Option
from gunicorn.app.base import Application as GunicornApplication
from gunicorn.config import Config as GunicornConfig
import statsd
from onyx.environment import Environment


CONFIG_PATH_LOCATIONS = ['/etc/onyx', abspath(dirname(__file__))]

def environment_manager_create(config=None):
    """
    Create and configure application
    If not specified, the default config will be loaded.
    If the ONYX_SETTINGS is provided, the file location will take precedence
    """

    for path in CONFIG_PATH_LOCATIONS:
        sys.path.append(path)

    if config is None:
        # None will be passed by manage.py.
        # A default param value will get overwritten, so this is implemented here.
        config = 'onyx.default_settings.DefaultConfig'

    config = os.environ.get('ONYX_SETTINGS', config)

    env = Environment.instance(config)
    from onyx.webapp import setup_routes
    setup_routes(env.application)

    return env.application


class RFC3339Formatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        d = datetime.utcnow()
        return d.strftime("%Y-%m-%dT%H:%M:%S") + "Z"


class GunicornServerCommand(Command):
    """
    Run the Onyx Server using gunicorn
    """
    def __init__(self, host='127.0.0.1', port=5000, workers=1,
                 access_logfile='-', max_requests=0, debug=True):
        self.options = {
            "host": host,
            "port": port,
            "workers": workers,
            "access_logfile": access_logfile,
            "max_requests": max_requests,
            "debug": debug,
        }

    def get_options(self):
        options = (
            Option('-H', '--host',
                   dest='host',
                   type=str,
                   default=self.options['host'],
                   help="hostname to bind server to"),
            Option('-p', '--port',
                   dest='port',
                   type=int,
                   default=self.options['port'],
                   help="port to bind server to"),
            Option('-w', '--workers',
                   dest='workers',
                   type=int,
                   default=self.options['workers'],
                   help="set the number of workers"),
            Option('--access-logfile',
                   dest='access_logfile',
                   type=str,
                   default=self.options['access_logfile'],
                   help="set the access log output location"),
            Option('--max-requests',
                   dest='max_requests',
                   type=int,
                   default=self.options['max_requests'],
                   help="set the maximum number of requests " +
                        "to serve before reloading"),
            Option('--no-debug',
                   dest='debug',
                   action='store_false',
                   default=self.options['debug'],
                   help="turn off debug mode"),
        )
        return options

    def run(self, **kwargs):
        self.options.update(kwargs)
        if not kwargs.get('debug'):
            self.options['workers'] = multiprocessing.cpu_count() * 2 + 1

        options = self.options

        class GunicornServer(GunicornApplication):
            def init(self, **kwargs):
                config = {
                    'bind': '{0}:{1}'.format(
                        options['host'],
                        options['port']
                    ),
                    'workers': options['workers'],
                    'worker_class': 'gevent',
                    'accesslog': options['access_logfile'],
                    'max_requests': options['max_requests'],
                }
                return config

            def load(self):
                # Step needed to get around flask's import time side-effects
                app = environment_manager_create()
                return app

            def load_config(self):
                # Overriding to prevent Gunicorn from reading
                # the command-line arguments
                self.cfg = GunicornConfig(self.usage, prog=self.prog)
                cfg = self.init()
                if cfg and cfg is not None:
                    for k, v in cfg.items():
                        self.cfg.set(k.lower(), v)

        GunicornServer().run()
