import sys
import importlib
import logging

from flask import Flask
from flask_sslify import SSLify
from mock import Mock
from statsd import StatsClient


class EnvironmentUninitializedError(Exception): pass


class Environment(object):

    def __init__(self, config_filename):
        self.__config_filename = config_filename
        self.config = self.load_config_obj(config_filename)
        self.__application = None
        self.statsd = None
        self.init()
        if not hasattr(Environment, "_instance"):
            Environment._instance = self

    def load_config_obj(self, obj_name):
        tokens = obj_name.split(".")
        module_name = ".".join(tokens[:-1])
        class_name = tokens[-1]
        module = importlib.import_module(module_name)
        return getattr(module, class_name)

    @property
    def is_debug(self):
        return self.config.DEBUG

    @property
    def is_test(self):
        return self.config.ENVIRONMENT == "test"

    @property
    def is_development(self):
        return self.config.ENVIRONMENT == "dev"

    @property
    def is_production(self):
        return self.config.ENVIRONMENT == "prod"

    @property
    def application(self):
        if not self.__application:
            raise EnvironmentUninitializedError("Cannot obtain application without initializing environment")
        return self.__application

    def _setup_logger(self):
        """
        Setup and return a logger configured to return a timestamp in RFC3339 format
        The timestamp is always UTC
        """
        handler = logging.StreamHandler(sys.stdout)
        from onyx.utils import RFC3339Formatter
        fmt = RFC3339Formatter("%(asctime)-19s %(levelname)-8s %(message)s")
        handler.setFormatter(fmt)
        logger = logging.getLogger('onyx')
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def log(self, logger, type, message, level=logging.INFO):
        """
        Special formatter that logs messages in a format log parsers expects
        """
        msg = " ".join([logger, type, message])
        self.logger.log(level, msg)

    def init(self):
        """
        Start point for application configuration
        """
        ### logging
        if self.is_test:
            self.logger = Mock()
            self.statsd = Mock()
        else:
            self.logger = self._setup_logger()
            self.statsd = StatsClient(**self.config.STATSD)

        # Application server setup
        app = Flask('onyx')
        SSLify(app, subdomains=True, permanent=True)
        app.config.from_object(self.__config_filename)

        if app.config['ENVIRONMENT'] not in app.config['STATIC_ENABLED_ENVS']:
            app.config['STATIC_FOLDER'] = None
        self.__application = app

        return app

    @classmethod
    def instance(cls, config=None):
        if hasattr(Environment, "_instance") and config is None:
            return Environment._instance
        elif config is not None:
            return Environment(config)

        raise EnvironmentUninitializedError("Cannot obtain instance if uninitialized")
