from onyx.utils import environment_manager_create
from flask.ext.testing import TestCase

class BaseTestCase(TestCase):

    def create_app(self):
        self.app = environment_manager_create()
        return self.app
