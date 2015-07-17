import gevent
from nose.tools import assert_equals
from mock import Mock, MagicMock
import onyx.environment
from onyx.environment import Environment, _read_tile_index_loop
from tests.base import BaseTestCase


class TestReadLoop(BaseTestCase):

    def test_v3_index(self):
        """
        Test reading v3 tile indexes
        """
        env = Environment.instance()

        env.config = Mock()
        env.config.TILE_INDEX_FILES = {'desktop': 'some_url'}

        v3_data = {'STAR/en-US': {'legacy': 'data'}, '__ver__': 3}

        class TestResponse:
            status_code = 200

            def json(self):
                return v3_data

        onyx.environment.grequests.map = Mock(return_value=[TestResponse()])

        index_mock = MagicMock()
        env.config.LINKS_LOCALIZATIONS = index_mock

        gevent.spawn(_read_tile_index_loop, env)

        gevent.sleep(0)  # make the event loop tick
        index_mock.__setitem__.assert_called_with('desktop', v3_data)

    def test_index_failure(self):
        """
        Test json file read failure
        """
        env = Environment.instance()

        env.config = Mock()
        env.config.TILE_INDEX_FILES = {'desktop': 'some_url'}
        env.log_dict = Mock()

        class TestResponse:
            status_code = 200

            def json(self):
                raise Exception("error")

        onyx.environment.grequests.map = Mock(return_value=[TestResponse()])

        index_mock = MagicMock()
        env.config.LINKS_LOCALIZATIONS = index_mock

        gevent.spawn(_read_tile_index_loop, env)

        gevent.sleep(0)  # make the event loop tick
        assert_equals(0, index_mock.call_count)

        env.log_dict.assert_any_calls()
        assert_equals('gevent_tiles_payload_error', env.log_dict.call_args[1]['action'])

    def test_index_request_server_error(self):
        """
        Test request server error
        """
        env = Environment.instance()

        env.config = Mock()
        env.config.TILE_INDEX_FILES = {'desktop': 'some_url'}
        env.log_dict = Mock()

        class TestResponse:
            status_code = 500

            def json(self):
                assert(False)

        onyx.environment.grequests.map = Mock(return_value=[TestResponse()])

        index_mock = MagicMock()
        env.config.LINKS_LOCALIZATIONS = index_mock

        gevent.spawn(_read_tile_index_loop, env)

        gevent.sleep(0)  # make the event loop tick
        assert_equals(0, index_mock.call_count)

        env.log_dict.assert_any_calls()
        assert_equals('gevent_tiles_server_update_error', env.log_dict.call_args[1]['action'])

    def test_index_request_correctness(self):
        """
        Test requests are correct and executed in the right order
        """
        env = Environment.instance()

        key_mirror = {
            'desktop': 'http://desktop.url',
            'desktop-prerelease': 'http://desktop-prerelease.url',
            'android': 'http://android.url',
            'hello': 'http://hello.url'
        }

        env.config = Mock()
        env.config.TILE_INDEX_FILES = key_mirror
        env.log_dict = Mock()

        class TestResponse:
            status_code = 200

            def __init__(self, url):
                self.url = url

            def json(self):
                # instead of JSON data, return a URL
                return self.url

        def map_response(*args, **kwargs):
            urls = args[0]
            output = []
            for url in urls:
                output.append(TestResponse(url))
            return output

        def get_response(*args, **kwargs):
            return args[0]

        onyx.environment.grequests.map = Mock(side_effect=map_response)
        onyx.environment.grequests.get = Mock(side_effect=get_response)

        env.config.LINKS_LOCALIZATIONS = {
            'desktop': None,
            'desktop-prerelease': None,
            'android': None,
            'hello': None
        }

        gevent.spawn(_read_tile_index_loop, env)

        gevent.sleep(0)  # make the event loop tick

        env.log_dict.assert_no_calls()
        assert_equals(key_mirror, env.config.LINKS_LOCALIZATIONS)

    def test_index_request_failure(self):
        """
        Test request failure
        """
        env = Environment.instance()

        env.config = Mock()
        env.config.TILE_INDEX_FILES = {'desktop': 'some_url'}
        env.log_dict = Mock()

        map_mock = Mock()
        map_mock.side_effect = Exception('some grequests error')
        onyx.environment.grequests.map = map_mock

        index_mock = MagicMock()
        env.config.LINKS_LOCALIZATIONS = index_mock

        gevent.spawn(_read_tile_index_loop, env)

        gevent.sleep(0)  # make the event loop tick
        assert_equals(0, index_mock.call_count)

        env.log_dict.assert_any_calls()
        assert_equals('gevent_tiles_request_error', env.log_dict.call_args[1]['action'])
