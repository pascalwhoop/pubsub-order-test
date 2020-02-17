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

"""
Tests assume a running redis instance on port 6379. Run one with
```
docker run --name some-redis -p 6379:6379 redis
```
"""

class TestMain(unittest.TestCase):

    def setUp(self):
        main.r.flushdb()

    def test_redis(self):
        assert main.r.get("test") is None
        main.r.set("test", "foo")
        assert main.r.get("test") == "foo"

    def test_get_state(self):
        res = main.get_state()
        assert isinstance(res, Response)
        res_json = res.get_json()
        assert len(res_json.values()) == 0
        main.r.set("2020xx", "foo")
        assert len(main.get_state().get_json().values()) == 1

    def test_id_key(self):
        k = main._id_key("foo")
        assert ":foo" in k

    def test_handle_step(self):
        for i in [1,2,4,3,5,6,7,9,8]:
            main._handle_step(_step_message(i))
        st = _state_from_redis()
        print(st)
        assert int(st[f"{main._id_key(0)}.ooo"])   == 5
        assert int(st[f"{main._id_key(0)}.last"])  == 8
        # if it's O, it cannot be I anymore because O is worse than I
        #assert int(st[f"{main._id_key(0)}.ooi"])   == 4
        assert int(st[f"{main._id_key(0)}.total"]) == 9
        #assert main.state.stage_stats.get(STAGE) is None
        #main._validate_ready(STAGE)
        #assert main.state.stage_stats[STAGE] is not None

        #for i in [1,2,4,3]:
        #    main._handle_step(_step_message(i))
        #assert main.state.stage_stats[STAGE].out_of_index_count == 2
        #assert main.state.stage_stats[STAGE].out_of_order_count == 2

        #main._reset_state()
        #main._validate_ready(STAGE)
        #for i in [2,3,4,5,6,1]: #late 1
        #    main._handle_step(_step_message(i))
        #assert main.state.stage_stats[STAGE].out_of_index_count == 6
        #assert main.state.stage_stats[STAGE].out_of_order_count == 2
        #main._reset_state()

    #def test_handle_inner_message_start(self):
    #    # test start resets
    #    msg = {
    #        "type": "start"
    #    }
    #    a = main.state
    #    main._handle_inner_message(msg)
    #    b = main.state
    #    assert a is b
    
    #@patch("main.log")
    #def test_handle_inner_message_end(self, log_mock):
    #    # test start resets
    #    msg = {
    #        "type": "end"
    #    }
    #    main._handle_inner_message(msg)
    #    assert log_mock.info.call_count == 1
    #    assert log_mock.warning.call_count == 1

    def test_handle_message_json(self):
        msg = json.load(open(rel_path(__file__, "test_request.json")))
        inside_message = main._handle_message_json(msg)
        print(inside_message)
        assert isinstance(inside_message, dict)
        assert "==" not in inside_message


    def test_handle_whole_flow(self):
        id = main._id_key(STAGE)
        [main._handle_inner_message(_step_message(i, STAGE)) for i in range(1,50)]
        assert int(_state_from_redis()[f"{id}.total"]) == 49

def _step_message(i, stage=0):
    return {
        "stage": stage,
        "counter": i,
        "sleep_length": 0,
        "type": "step"
    }

def _state_from_redis():
    return main.get_state().get_json()

def dir_path(file: str) -> str:
    return os.path.dirname(os.path.abspath(file))


def rel_path(file: str, relative_path: str) -> str:
    dir_ = dir_path(file)
    return os.path.abspath(os.path.join(dir_, relative_path))