import json
from flask import url_for
from nose.tools import (
    assert_equals,
    assert_is_none
)
from tests.base import BaseTestCase


class TestNewtabServing(BaseTestCase):

    def test_missing_payload(self):
        """
        A call without a payload errors
        """
        response = self.client.post(url_for('v1_links.fetch'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")])
        assert_equals(response.status_code, 400)
        assert_is_none(response.headers.get('Set-Cookie'))
        assert_equals(response.content_length, 0)

    def test_missing_dircount(self):
        """
        A call without directoryCount errors
        """
        response = self.client.post(url_for('v1_links.fetch'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")],
                                    data=json.dumps({'locale': 'en-US'}))
        assert_equals(response.status_code, 400)
        assert_is_none(response.headers.get('Set-Cookie'))
        assert_equals(response.content_length, 0)

    def test_unknown_locale(self):
        """
        A call with an unknown locale yields an HTTP 204 response
        """
        response = self.client.post(url_for('v1_links.fetch'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")],
                                    data=json.dumps({'locale': 'zh-CN', 'directoryCount': {"organic": 1}}))
        assert_equals(response.status_code, 204)
        assert_equals(response.content_length, 0)

    def test_success(self):
        """
        A call with an known geo/locale pair redirects
        """
        response = self.client.post(url_for('v1_links.fetch'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")],
                                    environ_base={"REMOTE_ADDR": "173.194.43.105"},
                                    data=json.dumps({'locale': 'en-US', 'directoryCount': {'organic': 1}}))
        assert_equals(response.status_code, 303)
        assert_equals(response.content_length, 0)
