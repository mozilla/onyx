from onyx.utils import environment_manager_create
from onyx.default_settings import DefaultConfig
from flask.ext.testing import TestCase
from onyx.environment import Environment


class BaseTestCase(TestCase):

    def create_app(self):
        DefaultConfig.ENVIRONMENT = 'test'
        self.app = environment_manager_create()
        env = Environment.instance()
        env.config.LINKS_LOCALIZATIONS = {
            "STAR/en-US": "http://valid.url.com"
        }
        return self.app
