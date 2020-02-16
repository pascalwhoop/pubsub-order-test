from flask import Flask, request, Response, jsonify
import json
from json import JSONEncoder
import logging as log
import base64
from dataclasses import dataclass
from collections import defaultdict



# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

@dataclass
class State:
    current_stage: str
    stage_stats: dict
    
@dataclass
class StageStats:
    out_of_index_count: int=0
    out_of_order_count: int=0
    total_received    : int=0
    last_counter      : int=0

state: State = None
def _reset_state():
    global state
    state = State(current_stage= "start", stage_stats={})
_reset_state()


@app.route('/state', methods=["GET"])
def get_state():
    return Response(json_encoder.encode(state), mimetype="application/json")

@app.route('/push', methods=["POST"])
def push():
    if request.json is None:
        return Response(status=400)
    else:
        msg = _handle_message_json(request.json)
        return _handle_inner_message(msg)
    
    
    
def _handle_inner_message(msg):
    if msg["type"] == "start":
        log.warning("received start message")
    elif msg["type"] == "end":
        log.warning("received start end")
        # TODO make statistics
        log.info(json_encoder.encode(state))
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
        log.warning(f"OOIC ++ : msg counter: {now_counter}, system counter: {stats.total_received}")
    if stats.last_counter +1 != now_counter:
        stats.out_of_order_count += 1
        log.warning(f"OOOC ++ : last received: {stats.last_counter}, msg counter: {now_counter}")
    
    stats.last_counter = now_counter
    

class DataClassEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__
json_encoder = DataClassEncoder()

def _handle_message_json(msg_json) -> dict:
    base_bytes = msg_json["message"]["data"].encode()
    return json.loads(base64.decodebytes(base_bytes).decode("utf-8"))


def _validate_ready(stage):
    if stage not in state.stage_stats:
        state.stage_stats[stage] = StageStats()



if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]

