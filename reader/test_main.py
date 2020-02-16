# Copyright 2018 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import main
import unittest
import json
from flask import Response
import os
from unittest.mock import patch
STAGE = 0

class TestMain(unittest.TestCase):

    def test_get_state(self):
        res = main.get_state()
        assert isinstance(res, Response)
        assert res.get_json()["current_stage"] == "start"

    def test_handle_step(self):
        assert main.state.stage_stats.get(STAGE) is None
        main._validate_ready(STAGE)
        assert main.state.stage_stats[STAGE] is not None

        for i in [1,2,4,3]:
            main._handle_step(_step_message(i))
        assert main.state.stage_stats[STAGE].out_of_index_count == 2
        assert main.state.stage_stats[STAGE].out_of_order_count == 2

        main._reset_state()
        main._validate_ready(STAGE)
        for i in [2,3,4,5,6,1]: #late 1
            main._handle_step(_step_message(i))
        assert main.state.stage_stats[STAGE].out_of_index_count == 6
        assert main.state.stage_stats[STAGE].out_of_order_count == 2
        main._reset_state()

    def test_handle_inner_message_start(self):
        # test start resets
        msg = {
            "type": "start"
        }
        a = main.state
        main._handle_inner_message(msg)
        b = main.state
        assert a is b
    
    @patch("main.log")
    def test_handle_inner_message_end(self, log_mock):
        # test start resets
        msg = {
            "type": "end"
        }
        main._handle_inner_message(msg)
        assert log_mock.info.call_count == 1
        assert log_mock.warning.call_count == 1

    def test_handle_message_json(self):
        msg = json.load(open(rel_path(__file__, "test_request.json")))
        inside_message = main._handle_message_json(msg)
        print(inside_message)
        assert isinstance(inside_message, dict)
        assert "==" not in inside_message


    def test_handle_whole_flow(self):
        [main._handle_inner_message(_step_message(i, 0)) for i in range(1,50)]
        assert main.state.stage_stats[0].out_of_index_count == 0
        [main._handle_inner_message(_step_message(i, 1)) for i in range(1,50)]
        assert main.state.stage_stats[1].out_of_index_count == 0
        [main._handle_inner_message(_step_message(i, 2)) for i in range(1,50)]
        assert main.state.stage_stats[2].out_of_index_count == 0
        [main._handle_inner_message(_step_message(i, 3)) for i in range(1,50)]
        assert main.state.stage_stats[3].out_of_index_count == 0
        assert len(main.state.stage_stats) == 4

def _step_message(i, stage=0):
    return {
        "stage": stage,
        "counter": i,
        "sleep_length": 0,
        "type": "step"
    }


def dir_path(file: str) -> str:
    return os.path.dirname(os.path.abspath(file))


def rel_path(file: str, relative_path: str) -> str:
    dir_ = dir_path(file)
    return os.path.abspath(os.path.join(dir_, relative_path))