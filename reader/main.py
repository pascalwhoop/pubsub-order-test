# Copyright 2018 Google LLC
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

# [START gae_python37_app]
from flask import Flask, request, Response
import json


# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

class State:
    def __init__(self):
        self.current_stage = "start"
        self.stage_stats = {}
    
class StageStats:
    def __init__(self):
        self.out_of_index_count=0
        self.out_of_order_count=0
        self.total_received=0
        self.last_counter=0

state = State()

@app.route('/push', methods=["POST"])
def push():
    msg = _handle_message_json(request.json)
    return _handle_inner_message(msg)
    
    
    
def _handle_inner_message(msg):
    if msg["type"] == "start":
        pass
    elif msg["type"] == "end":
        # TODO make statistics
        pass
    elif msg["type"] == "step":
        _validate_ready(msg["stage"])
        _handle_step(msg)
    return Response(status=200)



def _handle_step(msg):
    """
    actually receives the message, not the container. Increments everything
    """
    stats = state.stage_stats[msg["stage"]]
    stats.total_received += 1
    now_counter = msg["counter"]
    # check if message "in the right spot"
    # 1 2 3 4 == 0
    # 1 3 2 4 == 2
    # 3 4 1 2 == 4
    # 2 3 4 1 == 4
    # 2 1 4 3 == 4 
    # messages are out of order if they are not in their right index
    if now_counter != stats.total_received:
        stats.out_of_index_count += 1
    if stats.last_counter +1 != now_counter:
        stats.out_of_order_count += 1
    
    stats.last_counter = now_counter
    


def _handle_message_json(msg_json) -> dict:
    json.loads(msg_json["message"]["data"].decode("utf-8"))


def _validate_ready(stage):
    if stage not in state.stage_stats:
        state.stage_stats[stage] = StageStats()


def _reset_state():
    global state
    state = State()

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]
