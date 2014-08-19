import json
from copy import deepcopy
from datetime import datetime, timedelta
import calendar
from onyx.encryption import encrypt, decrypt
from flask import url_for
from flask.sessions import SecureCookieSessionInterface
from nose.tools import (
    assert_equals,
    assert_is_not_none,
    assert_is_none,
    assert_not_equals
)
from werkzeug.http import parse_cookie
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
        assert_equals(int(response.headers.get('Content-Length')), 0)

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
        assert_equals(int(response.headers.get('Content-Length')), 0)

    def test_unknown_locale(self):
        """
        A call with an unknown locale yields an HTTP 204 response
        """
        response = self.client.post(url_for('v1_links.fetch'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")],
                                    data=json.dumps({'locale': 'zh-CN', 'directoryCount': {"organic": 1}}))
        assert_equals(response.status_code, 204)
        assert_equals(int(response.headers.get('Content-Length')), 0)

    def test_success(self):
        """
        A call with an unknown locale yields an HTTP 204 response
        """
        response = self.client.post(url_for('v2_links.fetch'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")],
                                    data=json.dumps({'locale': 'en-US', 'directoryCount': {'organic': 1}}))
        assert_equals(response.status_code, 303)
