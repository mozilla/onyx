import os
import json
import gevent
from tempfile import NamedTemporaryFile
from nose.tools import assert_equals
from mock import Mock, PropertyMock
from onyx.environment import Environment, _convert_legacy_index, _read_tile_index_loop
from tests.base import BaseTestCase


class TestTileIndexFormats(BaseTestCase):

    def test_legacy_format(self):
        """
        Tests legacy tile index format
        """
        converted = _convert_legacy_index({'STAR/en-US': 'https://example.com/en-US-distro.json'})
        assert_equals({'STAR/en-US': {'legacy': 'https://example.com/en-US-distro.json'}}, converted)


class TestReadLoop(BaseTestCase):

    def test_read_legacy(self):
        """
        Test reading legacy tile indexes
        """
        env = Environment.instance()
        test_file = NamedTemporaryFile()

        env.config = Mock()
        env.config.TILE_INDEX_DIR, env.config.TILE_INDEX_FILE = os.path.split(test_file.name)

        json.dump({'STAR/en-US': 'https://example.com/en-US-distro.json'}, test_file)
        test_file.flush()

        index_mock = PropertyMock()
        type(env.config).LINKS_LOCALIZATIONS = index_mock

        gevent.spawn(_read_tile_index_loop, env)

        gevent.sleep(0)  # make the event loop tick
        index_mock.assert_any_call({'STAR/en-US': {'legacy': 'https://example.com/en-US-distro.json'}})

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
