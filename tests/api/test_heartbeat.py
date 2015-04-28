from flask import url_for
from nose.tools import assert_equals
from tests.base import BaseTestCase


class TestHeartBeat(BaseTestCase):

    def test_ok(self):
        """
        """
        response = self.client.get(url_for('heartbeat.report'))
        assert_equals(response.status_code, 200)
