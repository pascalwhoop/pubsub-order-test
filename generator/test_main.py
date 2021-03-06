import unittest
import main
import json
from unittest.mock import MagicMock
from unittest.mock import patch
from datetime import timedelta
from os import environ


class TestMain(unittest.TestCase):
    def test_main_loop(self):
        mock_callable = MagicMock()

        main.main_loop(mock_callable, duration=timedelta(seconds=1), nth=100)
        assert mock_callable.publish.call_count > 1
        assert mock_callable.publish.call_count < 100 #cannot send more than 100 messages if we sleep 1/100th

    def test_make_message(self):
        obj = main._make_message(1, 2, 3)
        print(obj)
        assert obj["stage"] is 1
        assert obj["sleep_length"] is 2
        assert obj["counter"] is 3
