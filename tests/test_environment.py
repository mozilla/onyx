import os
import json
import gevent
from tempfile import NamedTemporaryFile
from nose.tools import assert_equals
from mock import Mock, PropertyMock
from onyx.environment import Environment, _read_tile_index_loop
from tests.base import BaseTestCase


class TestReadLoop(BaseTestCase):

    def test_v3_index(self):
        """
        Test reading v3 tile indexes
        """
        env = Environment.instance()
        test_file = NamedTemporaryFile()

        env.config = Mock()
        env.config.TILE_INDEX_DIR, env.config.TILE_INDEX_FILE = os.path.split(test_file.name)

        v3_data = {'STAR/en-US': {'legacy': 'data'}, '__ver__': 3}
        json.dump(v3_data, test_file)
        test_file.flush()

        index_mock = PropertyMock()
        type(env.config).LINKS_LOCALIZATIONS = index_mock

        gevent.spawn(_read_tile_index_loop, env)

        gevent.sleep(0)  # make the event loop tick
        index_mock.assert_any_call(v3_data)

    def test_index_failure(self):
        """
        Test json file read failure
        """
        env = Environment.instance()
        test_file = NamedTemporaryFile()

        env.config = Mock()
        env.config.TILE_INDEX_DIR, env.config.TILE_INDEX_FILE = os.path.split(test_file.name)
        env.log_dict = Mock()

        v3_data = "{'STAR/en-US': {'legacy': 'data'}, '__ver__': 3"
        test_file.write(v3_data)
        test_file.flush()

        index_mock = PropertyMock()
        type(env.config).LINKS_LOCALIZATIONS = index_mock

        gevent.spawn(_read_tile_index_loop, env)

        gevent.sleep(0)  # make the event loop tick
        assert_equals(0, index_mock.call_count)

        env.log_dict.assert_any_calls()
        assert_equals('gevent_tiles_update_error', env.log_dict.call_args[1]['action'])
