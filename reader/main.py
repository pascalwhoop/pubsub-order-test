from flask import Flask, request, Response, jsonify
import json
from json import JSONEncoder
import logging as log
import base64
from dataclasses import dataclass
from collections import defaultdict
from os import environ
from datetime import datetime
import redis


REDIS_HOST = environ.get("redis_host", "localhost")
REDIS_PORT = environ.get("redis_port", "6379")
r = redis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), db=0, decode_responses=True, encoding="utf-8")
DATE_FORMAT = "%Y%m%d"


# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

ooo_key   = "{}.ooo"
ooi_key   = "{}.ooi"
total_key = "{}.total"
last_key  = "{}.last"
hist_key  = "{}.hist"

@app.route('/state', methods=["GET"])
def get_state():
    keys = r.keys("2020*")
    data  = {key:r.get(key) for key in keys}

    
    return Response(json.dumps(data), mimetype="application/json")

@app.route('/reset', methods=["POST"])
def reset():
    r.flushdb()
    return Response(status=200)

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
    elif msg["type"] == "step":
        _handle_step(msg)
    return Response(status=200)


def _id_key(stage) -> str:
    # this assumes that each stage gets run at most 1x per hour. See `scheduler.tf` for details
    return f"{datetime.now().strftime(DATE_FORMAT)}:{stage}"

def _handle_step(msg):
    """
    actually receives the message, not the container. Increments everything

     check if message "in the right spot"
     1 2 3 4 == 0
     1 3 2 4 == 2
     3 4 1 2 == 4
     2 3 4 1 == 4
     2 1 4 3 == 4 
     messages are out of order if they are not in their right index
    all went perfectly
    """
    msg_counter = msg["counter"]
    id = _id_key(msg["stage"])
    #increment by one
    db_total = r.incr  (total_key.format(id))
    db_last  = r.getset(last_key.format(id), msg_counter)

    if db_last is None:
        #first message -> skip
        _log_hist(id)
        return
    db_last = int(db_last)

    if  db_last +1 == msg_counter and db_total == msg_counter:
        _log_hist(id)

    # not same number as what we received so far
    if msg_counter != db_total:
        r.incr(ooi_key.format(id))
        log.warning(f"OOIC ++ : msg counter: {msg_counter}, system counter: {db_total}")
        #stats.events.append("I")

    # previous message was not -1 of current
    if db_last +1 != msg_counter:
        r.incr(ooo_key.format(id))
        log.warning(f"OOOC ++ : last received: {db_last}, msg counter: {msg_counter}")
        _log_hist(id, "O")
    
    
def _log_hist(id, ev="."):
    """
    log an event to the history key in redis.
    . == as expected
    O == out of order
    """
    r.append(hist_key.format(id), ev)


def _handle_message_json(msg_json) -> dict:
    base_bytes = msg_json["message"]["data"].encode()
    return json.loads(base64.decodebytes(base_bytes).decode("utf-8"))


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]

