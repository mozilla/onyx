import json
from flask import url_for
from nose.tools import assert_equals
from tests.base import BaseTestCase


LINK_ACTIVITY_STREAM_V4 = "v4_links.activity_stream"
LINK_ACTIVITY_STREAM_V4_CSP = "v4_links.activity_stream_csp"


class TestActivityStreamPing(BaseTestCase):
    def test_missing_payload(self):
        response = self.client.post(url_for(LINK_ACTIVITY_STREAM_V4),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")])
        assert_equals(response.status_code, 400)
        assert_equals(response.content_length, 0)

    def test_junk_payload(self):
        response = self.client.post(url_for(LINK_ACTIVITY_STREAM_V4),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")],
                                    data='"hfdsfdsjkl"')
        assert_equals(response.status_code, 400)
        assert_equals(response.content_length, 0)

    def test_payload_meta(self):
        response = self.client.post(url_for(LINK_ACTIVITY_STREAM_V4),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")],
                                    data=json.dumps({"data": "test", "action": "activity_stream_session"}))
        assert_equals(response.status_code, 200)
        assert_equals(response.content_length, 0)


class TestActivityStreamCSP(BaseTestCase):
    def test_missing_payload(self):
        response = self.client.post(url_for(LINK_ACTIVITY_STREAM_V4_CSP),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")])
        assert_equals(response.status_code, 400)
        assert_equals(response.content_length, 0)

    def test_junk_payload(self):
        response = self.client.post(url_for(LINK_ACTIVITY_STREAM_V4_CSP),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")],
                                    data='"hfdsfdsjkl"')
        assert_equals(response.status_code, 400)
        assert_equals(response.content_length, 0)

    def test_payload_meta(self):
        response = self.client.post(url_for(LINK_ACTIVITY_STREAM_V4_CSP),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")],
                                    data=json.dumps({"csp-report": {"document-uri": "http://example.com/page.html"}}))
        assert_equals(response.status_code, 200)
        assert_equals(response.content_length, 0)
