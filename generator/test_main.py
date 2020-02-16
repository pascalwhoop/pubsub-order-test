import unittest
import main
import json
from unittest.mock import MagicMock
from unittest.mock import patch
from os import environ


class TestMain(unittest.TestCase):
    def test_main_loop(self):
        mock_callable = MagicMock()

        main.main_loop(mock_callable, duration=1, nth=100)
        assert mock_callable.publish.call_count > 1

    def test_make_message(self):
        obj = main._make_message(1, 2, 3)
        print(obj)
        assert obj["stage"] is 1
        assert obj["sleep_length"] is 2
        assert obj["counter"] is 3
