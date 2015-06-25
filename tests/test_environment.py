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
        assert_equals('gevent_tiles_update_error', env.log_dict.call_args[1]['action'])
