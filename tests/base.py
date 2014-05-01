from onyx.utils import environment_manager_create
from onyx.default_settings import DefaultConfig
from flask.ext.testing import TestCase

class BaseTestCase(TestCase):

    def create_app(self):
        DefaultConfig.ENVIRONMENT = 'test'
        self.app = environment_manager_create()
        return self.app
