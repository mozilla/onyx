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
        A fetch call without a payload errors
        """
        response = self.client.post(url_for('v2_links.fetch'),
                                    content_type='application/json')
        assert_equals(response.status_code, 400)
        assert_is_none(response.headers.get('Set-Cookie'))
        assert_equals(int(response.headers.get('Content-Length')), 0)

    def test_unknown_locale(self):
        """
        A call with an unknown locale yields an HTTP 204 response
        """
        response = self.client.post(url_for('v2_links.fetch'),
                                    content_type='application/json',
                                    data=json.dumps({'locale': 'zh-CN'}))
        assert_equals(response.status_code, 204)
        assert_equals(int(response.headers.get('Content-Length')), 0)

class TestClickPing(BaseTestCase):

    def test_missing_payload(self):
        """
        A click ping call without a payload errors
        """
        response = self.client.post(url_for('v2_links.click'),
                                    content_type='application/json')
        assert_equals(response.status_code, 400)

    def test_empty_payload(self):
        """
        A click ping call with an empty payload errors
        """
        response = self.client.post(url_for('v2_links.click'),
                                    content_type='application/json',
                                    data=json.dumps({}))
        assert_equals(response.status_code, 400)

    def test_payload_meta(self):
        """
        A click ping succeeds
        """
        response = self.client.post(url_for('v2_links.click'),
                                    content_type='application/json',
                                    data=json.dumps({"data":"test"}))
        assert_equals(response.status_code, 200)
        assert_equals(int(response.headers.get('Content-Length')), 0)

class TestViewPing(BaseTestCase):

    def test_missing_payload(self):
        """
        A view ping call without a payload errors
        """
        response = self.client.post(url_for('v2_links.view'),
                                    content_type='application/json')
        assert_equals(response.status_code, 400)

    def test_empty_payload(self):
        """
        A view ping call with an empty payload errors
        """
        response = self.client.post(url_for('v2_links.view'),
                                    content_type='application/json',
                                    data=json.dumps({}))
        assert_equals(response.status_code, 400)

    def test_payload_meta(self):
        """
        A view ping succeeds
        """
        response = self.client.post(url_for('v2_links.view'),
                                    content_type='application/json',
                                    data=json.dumps({"data": "test"}))
        assert_equals(response.status_code, 200)
        assert_equals(int(response.headers.get('Content-Length')), 0)
