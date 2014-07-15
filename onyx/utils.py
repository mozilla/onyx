import sys
import multiprocessing
import logging
from flask import Flask
from flask_sslify import SSLify
from flask.ext.script import Command, Option
from gunicorn.app.base import Application as GunicornApplication
from gunicorn.config import Config as GunicornConfig
from heka.config import client_from_dict_config
from heka.holder import CLIENT_HOLDER
import onyx


APP_INSTANCE = None

def setup_debug_logger(logger_name):
    """
    Setup a stdout logger for debug mode
    """
    fmt = logging.Formatter("HEKA: [%(asctime)-15s] %(message)s")
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(fmt)
    logger = logging.getLogger(logger_name)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def create_app(config_filename):
    # TODO: forward proxy headers
    app = Flask(__name__)
    SSLify(app, subdomains=True, permanent=True)
    if not config_filename:
        app.config.from_object('onyx.default_settings.DefaultConfig')
    else:
        app.config.from_object(config_filename)

    if app.config['ENVIRONMENT'] not in app.config['STATIC_ENABLED_ENVS']:
        app.config['STATIC_FOLDER'] = None

    return app


def environment_manager_create(config=None):
    """
    Create and configure application
    """
    global APP_INSTANCE
    if not APP_INSTANCE:
        app = create_app(config)
        client = CLIENT_HOLDER.get_client(app.config['HEKA']['logger'])
        onyx.hekalog = client_from_dict_config(app.config['HEKA'], client)
        from onyx.webapp import setup_routes
        setup_routes(app)
        if app.config['ENVIRONMENT'] == 'dev':
            setup_debug_logger(app.config['HEKA']['logger'])
        APP_INSTANCE = app
    return APP_INSTANCE


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
            self.options['workers'] = multiprocessing.cpu_count()

        options = self.options

        class GunicornServer(GunicornApplication):
            def init(self):
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
