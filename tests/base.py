from onyx.utils import environment_manager_create
from onyx.default_settings import DefaultConfig
from flask.ext.testing import TestCase
from onyx.environment import Environment

DEFAULT_DATA = {
    'desktop': {
        'STAR/en-US': {
            'legacy': 'http://valid.url.com',
            'ag': 'http://valid.url.again.com',
        }
    }
}


class BaseTestCase(TestCase):

    def create_app(self):
        DefaultConfig.ENVIRONMENT = 'test'
        self.app = environment_manager_create()
        self.env = Environment.instance()
        self.env.config.LINKS_LOCALIZATIONS = DEFAULT_DATA
        return self.app

    def setUp(self):
        self.env.config.LINKS_LOCALIZATIONS = DEFAULT_DATA
