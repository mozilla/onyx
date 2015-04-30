import json
from flask import url_for
from nose.tools import assert_equals
from tests.base import BaseTestCase


class TestNewtabServing(BaseTestCase):

    def test_unknown_locale(self):
        """
        A call with an unknown locale yields an HTTP 204 response
        """
        response = self.client.get(
            url_for('v3_links.fetch', locale='zh-CN', channel='beta'),
            content_type='application/json',
            headers=[("User-Agent", "TestClient")])
        assert_equals(response.status_code, 204)
        assert_equals(int(response.headers.get('Content-Length')), 0)

    def test_unknown_country(self):
        """
        A call with an unknown country, but valid locale is success because of STAR
        """
        response = self.client.get(
            url_for('v3_links.fetch', locale='en-US', channel='beta'),
            content_type='application/json',
            headers=[("User-Agent", "TestClient")],
            environ_base={"REMOTE_ADDR": "202.224.135.69"})
        assert_equals(response.status_code, 303)

    def test_success(self):
        """
        A call with an known geo/locale pair redirects
        """
        response = self.client.get(
            url_for('v3_links.fetch', locale='en-US', channel='beta'),
            content_type='application/json',
            headers=[("User-Agent", "TestClient")],
            environ_base={"REMOTE_ADDR": "173.194.43.105"})
        assert_equals(response.status_code, 303)
        assert_equals(response.content_length, 0)


class TestClickPing(BaseTestCase):

    def test_missing_payload(self):
        """
        A click ping call without a payload errors
        """
        response = self.client.post(url_for('v3_links.click'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")])
        assert_equals(response.status_code, 400)

    def test_empty_payload(self):
        """
        A click ping call with an empty payload should pass
        """
        response = self.client.post(url_for('v3_links.click'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")],
                                    data=json.dumps({}))
        assert_equals(response.status_code, 200)

    def test_payload_meta(self):
        """
        A click ping succeeds
        """
        response = self.client.post(url_for('v3_links.click'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")],
                                    data=json.dumps({"data": "test"}))
        assert_equals(response.status_code, 200)
        assert_equals(int(response.headers.get('Content-Length')), 0)


class TestViewPing(BaseTestCase):

    def test_missing_payload(self):
        """
        A view ping call without a payload errors
        """
        response = self.client.post(url_for('v3_links.view'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")])
        assert_equals(response.status_code, 400)

    def test_junk_payload(self):
        """
        A view ping with valid json, but illegal payload (not a dict) errors
        """
        response = self.client.post(url_for('v3_links.view'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")],
                                    data='"hfdsfdsjkl"')
        assert_equals(response.status_code, 400)

    def test_payload_meta(self):
        """
        A view ping succeeds
        """
        response = self.client.post(url_for('v3_links.view'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")],
                                    data=json.dumps({"data": "test"}))
        assert_equals(response.status_code, 200)
        assert_equals(int(response.headers.get('Content-Length')), 0)
