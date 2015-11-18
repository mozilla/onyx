import json
from flask import url_for
from nose.tools import assert_equals, assert_true
from tests.base import BaseTestCase


class TestNewtabServing(BaseTestCase):

    def test_unknown_locale(self):
        """
        A call with an unknown locale yields an HTTP 204 response
        """
        response = self.client.get(
            url_for('v3_links.fetch', locale='zh-CN', channel='release'),
            content_type='application/json',
            headers=[("User-Agent", "TestClient")])
        assert_equals(response.status_code, 204)
        assert_equals(response.content_length, 0)

    def test_unknown_country(self):
        """
        A call with an unknown country, but valid locale is success because of STAR
        """
        response = self.client.get(
            url_for('v3_links.fetch', locale='en-US', channel='release'),
            content_type='application/json',
            headers=[("User-Agent", "TestClient")],
            environ_base={"REMOTE_ADDR": "202.224.135.69"})
        assert_equals(response.status_code, 303)
        assert_equals(response.content_length, 0)

    def test_success(self):
        """
        A call with an known geo/locale pair redirects
        """
        response = self.client.get(
            url_for('v3_links.fetch', locale='en-US', channel='release'),
            content_type='application/json',
            headers=[("User-Agent", "TestClient")],
            environ_base={"REMOTE_ADDR": "173.194.43.105"})
        assert_equals(response.status_code, 303)
        assert_equals(response.content_length, 0)

    def test_success_channel(self):
        """
        A fetch with different channels succeeds
        """

        self.env.config.LINKS_LOCALIZATIONS = {
            'desktop': {
                'STAR/en-US': {
                    'legacy': 'http://release.com',
                    'ag': 'http://release.com',
                }
            },
            'desktop-prerelease': {
                'STAR/en-US': {
                    'legacy': 'http://prerelease.com',
                    'ag': 'http://prerelease.com',
                }
            }
        }

        response = self.client.get(
            url_for('v3_links.fetch', locale='en-US', channel='release'),
            content_type='application/json',
            headers=[("User-Agent", "TestClient")],
            environ_base={"REMOTE_ADDR": "173.194.43.105"})
        assert_equals(response.status_code, 303)
        assert_equals(response.content_length, 0)
        assert_equals(response.headers['location'], 'http://release.com')

        response_beta = self.client.get(
            url_for('v3_links.fetch', locale='en-US', channel='beta'),
            content_type='application/json',
            headers=[("User-Agent", "TestClient")],
            environ_base={"REMOTE_ADDR": "173.194.43.105"})
        assert_equals(response_beta.status_code, 303)
        assert_equals(response_beta.content_length, 0)
        assert_equals(response_beta.headers['location'], 'http://prerelease.com')

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
            response = self.client.get(
                url_for('v3_links.fetch', locale='en-US', channel='release'),
                content_type='application/json',
                headers=[("User-Agent", "TestClient")],
                environ_base={"REMOTE_ADDR": "173.194.43.105"})
            assert_equals(response.status_code, 303)
            assert_equals(response.content_length, 0)
            assert_true(response.headers['location'] in distributions)
            dists.append(response.headers['location'])
            if len(set(dists)) == len(distributions):
                break
        assert_equals(set(distributions), set(dists))

    def test_channel_selection_buckets(self):
        """
        Test pre-release and release buckets
        """

        self.env.config.LINKS_LOCALIZATIONS = {
            'desktop': {
                'STAR/en-US': {
                    'legacy': 'http://release.com',
                    'ag': 'http://release.com',
                }
            },
            'desktop-prerelease': {
                'STAR/en-US': {
                    'legacy': 'http://prerelease.com',
                    'ag': 'http://prerelease.com',
                }
            },
            'android': {
                'STAR/en-US': {
                    'legacy': 'http://android.com',
                    'ag': 'http://android.com',
                }
            },
            'hello': {
                'STAR/en-US': {
                    'legacy': 'http://hello.com',
                    'ag': 'http://hello.com',
                }
            }
        }

        test_data = {
            'http://release.com': ('esr', 'release', 'bogus_release'),
            'http://prerelease.com': ('beta', 'aurora', 'nightly'),
            'http://android.com': ('android',),
            'http://hello.com': ('hello',)
        }

        for expected_location, channels in test_data.iteritems():

            for channel in channels:
                response = self.client.get(
                    url_for('v3_links.fetch', locale='en-US', channel=channel),
                    content_type='application/json',
                    headers=[("User-Agent", "TestClient")],
                    environ_base={"REMOTE_ADDR": "173.194.43.105"})
                assert_equals(response.status_code, 303)
                assert_equals(response.content_length, 0)
                assert_equals(response.headers['location'], expected_location)

    def test_channel_failure(self):
        """
        A channel configuration problem will throw a 500 error
        """
        self.env.config.LINKS_LOCALIZATIONS = {
        }

        channels = ('esr', 'release', 'beta', 'aurora', 'nightly', 'android',
                    'hello' 'bogus_release')

        for channel in channels:
            response = self.client.get(
                url_for('v3_links.fetch', locale='en-US', channel=channel),
                content_type='application/json',
                headers=[("User-Agent", "TestClient")],
                environ_base={"REMOTE_ADDR": "173.194.43.105"})
            assert_equals(response.status_code, 500)
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
        assert_equals(response.content_length, 0)

    def test_empty_payload(self):
        """
        A click ping call with an empty payload should pass
        """
        response = self.client.post(url_for('v3_links.click'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")],
                                    data=json.dumps({}))
        assert_equals(response.status_code, 200)
        assert_equals(response.content_length, 0)

    def test_payload_meta(self):
        """
        A click ping succeeds
        """
        response = self.client.post(url_for('v3_links.click'),
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
        response = self.client.post(url_for('v3_links.view'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")])
        assert_equals(response.status_code, 400)
        assert_equals(response.content_length, 0)

    def test_junk_payload(self):
        """
        A view ping with valid json, but illegal payload (not a dict) errors
        """
        response = self.client.post(url_for('v3_links.view'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")],
                                    data='"hfdsfdsjkl"')
        assert_equals(response.status_code, 400)
        assert_equals(response.content_length, 0)

    def test_payload_meta(self):
        """
        A view ping succeeds
        """
        response = self.client.post(url_for('v3_links.view'),
                                    content_type='application/json',
                                    headers=[("User-Agent", "TestClient")],
                                    data=json.dumps({"data": "test"}))
        assert_equals(response.status_code, 200)
        assert_equals(response.content_length, 0)
