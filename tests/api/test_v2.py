import json
from flask import url_for
from nose.tools import (
    assert_equals,
    assert_is_none,
    assert_true
)
from tests.base import BaseTestCase


class TestNewtabServing(BaseTestCase):

    def test_missing_payload(self):
        """
        A fetch call without a payload errors
        """
        response = self.client.post(url_for('v2_links.fetch'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")])
        assert_equals(response.status_code, 400)
        assert_is_none(response.headers.get('Set-Cookie'))
        assert_equals(response.content_length, 0)

    def test_unknown_locale(self):
        """
        A call with an unknown locale yields an HTTP 204 response
        """
        response = self.client.post(url_for('v2_links.fetch'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")],
                                    data=json.dumps({'locale': 'zh-CN'}))
        assert_equals(response.status_code, 204)
        assert_equals(response.content_length, 0)

    def test_unknown_country(self):
        """
        A call with an unknown country, but valid locale is success because of STAR
        """
        response = self.client.post(url_for('v2_links.fetch'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")],
                                    environ_base={"REMOTE_ADDR": "202.224.135.69"},
                                    data=json.dumps({'locale': 'en-US'}))
        assert_equals(response.status_code, 303)
        assert_equals(response.content_length, 0)

    def test_empty_payload(self):
        """
        A call with an empty empty json errors out b/c no locale is present
        """
        response = self.client.post(url_for('v2_links.fetch'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")],
                                    data=json.dumps({}))
        assert_equals(response.status_code, 400)
        assert_equals(response.content_length, 0)

    def test_channel_failure(self):
        """
        A channel configuration problem will throw a 500 error
        """
        self.env.config.LINKS_LOCALIZATIONS = {
        }
        response = self.client.post(url_for('v2_links.fetch'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")],
                                    environ_base={"REMOTE_ADDR": "173.194.43.105"},
                                    data=json.dumps({'locale': 'en-US', 'directoryCount': {'organic': 1}}))
        assert_equals(response.status_code, 500)
        assert_equals(response.content_length, 0)

    def test_success(self):
        """
        A call with an known geo/locale pair redirects
        """
        response = self.client.post(url_for('v2_links.fetch'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")],
                                    environ_base={"REMOTE_ADDR": "173.194.43.105"},
                                    data=json.dumps({'locale': 'en-US'}))
        assert_equals(response.status_code, 303)
        assert_equals(response.content_length, 0)

    def test_success_multiple_distribution(self):
        """
        A fetch to tile index with multiple distributions succeeds
        """

        distributions = ['http://release1.com', 'http://release2.com', 'http://release3.com']
        self.env.config.LINKS_LOCALIZATIONS = {
            'desktop': {
                'STAR/en-US': {
                    'legacy': distributions,
                    'ag': distributions
                }
            }
        }

        # fetching for finite times, we should be able to get all the possible distributions
        dists = []
        while True:
            response = self.client.post(
                url_for('v2_links.fetch'),
                content_type='application/json',
                headers=[("User-Agent", "TestClient")],
                environ_base={"REMOTE_ADDR": "173.194.43.105"},
                data=json.dumps({'locale': 'en-US'}))
            assert_equals(response.status_code, 303)
            assert_equals(response.content_length, 0)
            assert_true(response.headers['location'] in distributions)
            dists.append(response.headers['location'])
            if len(set(dists)) == len(distributions):
                break
        assert_equals(set(distributions), set(dists))


class TestClickPing(BaseTestCase):

    def test_missing_payload(self):
        """
        A click ping call without a payload errors
        """
        response = self.client.post(url_for('v2_links.click'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")])
        assert_equals(response.status_code, 400)
        assert_equals(response.content_length, 0)

    def test_empty_payload(self):
        """
        A click ping call with an empty payload should pass
        """
        response = self.client.post(url_for('v2_links.click'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")],
                                    data=json.dumps({}))
        assert_equals(response.status_code, 200)
        assert_equals(response.content_length, 0)

    def test_payload_meta(self):
        """
        A click ping succeeds
        """
        response = self.client.post(url_for('v2_links.click'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")],
                                    data=json.dumps({"data": "test"}))
        assert_equals(response.status_code, 200)
        assert_equals(response.content_length, 0)


class TestViewPing(BaseTestCase):

    def test_missing_payload(self):
        """
        A view ping call without a payload errors
        """
        response = self.client.post(url_for('v2_links.view'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")])
        assert_equals(response.status_code, 400)
        assert_equals(response.content_length, 0)

    def test_junk_payload(self):
        """
        A view ping with valid json, but illegal payload (not a dict) errors
        """
        response = self.client.post(url_for('v2_links.view'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")],
                                    data='"hfdsfdsjkl"')
        assert_equals(response.status_code, 400)
        assert_equals(response.content_length, 0)

    def test_payload_meta(self):
        """
        A view ping succeeds
        """
        response = self.client.post(url_for('v2_links.view'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")],
                                    data=json.dumps({"data": "test"}))
        assert_equals(response.status_code, 200)
        assert_equals(response.content_length, 0)
