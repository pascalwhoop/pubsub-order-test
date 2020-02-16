from flask import escape
from google.cloud import pubsub_v1
import os
import time
from datetime import datetime, timedelta
import json

TOPIC = os.environ.get("target_topic", "queue_topic")
PROJECT_NAME = os.environ.get("project_name", "quixotic-elf-256313")
TOPIC_PATH = f"projects/{PROJECT_NAME}/topics/{TOPIC}"
TRANS_DURATION = timedelta(seconds=int(os.environ.get("transmission_duration", "500")))


hour_mapping = {
    0: 0.5,
    1: 1,
    2: 2,
    3: 10,
    4: 50,
    5: 100,
}


def get_nth(stage):
    return hour_mapping[stage]


"""
trigger function. gets called and then generates a stream of messages in a sequential fashion
"""


def main(event, context):
    """Background Cloud Function to be triggered by Pub/Sub.
    Args:
         event (dict):  The dictionary with data specific to this type of
         event. The `data` field contains the PubsubMessage message. The
         `attributes` field will contain custom attributes if there are any.
         context (google.cloud.functions.Context): The Cloud Functions event
         metadata. The `event_id` field contains the Pub/Sub message ID. The
         `timestamp` field contains the publish time.
    """

    print("starting to send messages")
    publisher = pubsub_v1.PublisherClient()
    stage = datetime.now().hour % 6
    return main_loop(publisher, duration=TRANS_DURATION, nth=get_nth(stage), stage=stage)


def main_loop(publisher: pubsub_v1.PublisherClient, duration: timedelta, nth, stage):
    print(f"starting tranmission with {duration} duration per stage")
    _send(publisher, {"type": "start"})
    time.sleep(10)


    counter = 1
    print(f"stage {stage}, sending message every 1/{nth} second")
    finish_time = datetime.now() + duration
    while datetime.now() < finish_time:
        _send(publisher, _make_message(stage, nth, counter))
        counter += 1
        time.sleep(1 / nth)

    # _send(publisher, {"type": "end"})


# helper functions
# ----------------


def _send(p: pubsub_v1.PublisherClient, m) -> None:
    p.publish(TOPIC_PATH, str.encode(json.dumps(m)))


def _make_message(stage, sleep_length, counter) -> dict:
    return {
        "type": "step",
        "stage": stage,
        "sleep_length": sleep_length,
        "counter": counter,
    }
