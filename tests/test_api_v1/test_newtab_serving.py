import json
from copy import deepcopy
import base64
from datetime import datetime, timedelta
import calendar
from onyx.encryption import encrypt, decrypt
from flask import url_for
from flask.sessions import SecureCookieSessionInterface
from nose.tools import assert_equals, assert_is_not_none, assert_is_none, assert_not_equals, assert_true, assert_false
from werkzeug.http import parse_cookie, dump_cookie
from tests.base import BaseTestCase

class TestNewtabServing(BaseTestCase):

    def test_missing_payload(self):
        """
        A call without a payload errors
        """
        response = self.client.post(url_for('v1_links.newtab_serving'), content_type='application/json')
        assert_equals(response.status_code, 400)
        assert_is_none(response.headers.get('Set-Cookie'))
        assert_equals(int(response.headers.get('Content-Length')), 0)

    def test_missing_mime_type(self):
        """
        A call without a mimetype errors
        """
        response = self.client.post(url_for('v1_links.newtab_serving'), data=json.dumps({'locale':'en-US'}))
        assert_equals(response.status_code, 400)
        assert_is_none(response.headers.get('Set-Cookie'))
        assert_equals(int(response.headers.get('Content-Length')), 0)

    def test_unknown_locale(self):
        """
        A call with an unknown locale yields an HTTP 204 response
        """
        response = self.client.post(url_for('v1_links.newtab_serving'), content_type='application/json', data=json.dumps({'locale':'zh-CN'}))
        assert_equals(response.status_code, 204)
        assert_is_not_none(response.headers.get('Set-Cookie'))
        assert_equals(int(response.headers.get('Content-Length')), 0)

    def test_cookie_setting(self):
        """
        Cookies are set and unchanged if sent within a period
        """
        # sets cookie if not set
        response = self.client.post(url_for('v1_links.newtab_serving'), content_type='application/json', data=json.dumps({'locale':'en-US'}))
        assert_equals(response.status_code, 303)
        cookie = response.headers.get('Set-Cookie')
        assert_is_not_none(cookie)

        # cookie is unchanged after sending it again
        response = self.client.post(url_for('v1_links.newtab_serving'), content_type='application/json', data=json.dumps({'locale':'en-US'}))
        assert_equals(response.status_code, 303)
        assert_equals(response.headers.get('Set-Cookie'), cookie)

        with self.client.session_transaction() as session:
            assert_is_not_none(session.get('ciphertext'))
            assert_is_not_none(session.get('iv'))

    def test_cookie_reset(self):
        """
        Cookies are re-set when a certain time-period passes
        """
        # get original cookie
        response = self.client.post(url_for('v1_links.newtab_serving'), content_type='application/json', data=json.dumps({'locale':'en-US'}))

        cookie_str = response.headers.get('Set-Cookie')
        orig_cookie = parse_cookie(cookie_str)

        # create expired cookie
        cookie_handler = SecureCookieSessionInterface()
        signer = cookie_handler.get_signing_serializer(self.app)
        session = signer.loads(orig_cookie[self.app.config['SESSION_COOKIE_NAME']])
        original_data = json.loads(decrypt(session['ciphertext'], session['iv']))

        expired_data = deepcopy(original_data)

        expired_data['created'] = calendar.timegm((datetime.utcnow() - timedelta(days=self.app.config['SESSION_MAX_AGE'])).timetuple())

        ciphertext, iv = encrypt(json.dumps(expired_data))
        expired_signed_data = signer.dumps({'ciphertext':ciphertext, 'iv':iv})
        self.client.set_cookie('localhost.local', key=self.app.config['SESSION_COOKIE_NAME'], value=expired_signed_data)

        # send request with expired cookie
        response = self.client.post(url_for('v1_links.newtab_serving'), content_type='application/json', data=json.dumps({'locale':'en-US'}))
        new_cookie = response.headers.get('Set-Cookie')

        assert_not_equals(orig_cookie, new_cookie)

        new_data = None
        with self.client.session_transaction() as session:
            new_data = json.loads(decrypt(session['ciphertext'], session['iv']))

        assert_not_equals(new_data['sid'], expired_data['sid'])
        assert_not_equals(new_data['created'], expired_data['created'])
