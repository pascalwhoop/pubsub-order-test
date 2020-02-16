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
STAGE = 1

class TestMain(unittest.TestCase):

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

    def test_handle_whole_flow(self):
        pass
        # start
        # stage 1
        # stage 2
        # stop
        # validate stats are there

def _step_message(i):
    return {
        "stage": STAGE,
        "counter": i,
        "sleep_length": 0,
        "type": "step"
    }
