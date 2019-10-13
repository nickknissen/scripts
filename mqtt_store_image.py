#!/usr/bin/env python3
import re
import json
import argparse
import time




from typing import Any, Dict, NamedTuple

import paho.mqtt.client as mqtt


class MQTTListener:
    topic: str
    client: mqtt.Client

    def __init__(self, host, user, password, client_id, topic):
        self.topic = topic
        self.client = mqtt.Client(client_id)
        self.client.username_pw_set(user, password)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(host, 1883)

    def on_connect(self, client, userdata, flags, rc):
        self.client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        print("incomming message")
        f = open(f"images/output-{int(time.time())}.jpg", "wb")
        f.write(msg.payload)
        print("Image Received")
        f.close()



    def loop_forever(self):
        self.client.loop_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="copy data from mqtt to influxdb")

    parser.add_argument("--mqtt-address", dest="mqtt_address", default="localhost")
    parser.add_argument("--mqtt-user", dest="mqtt_user", required=True)
    parser.add_argument(
        "--mqtt-client", dest="mqtt_client", default="MQTTInfluxDBBridge"
    )
    parser.add_argument("--mqtt-password", dest="mqtt_password", required=True)
    parser.add_argument("--mqtt-topic", dest="mqtt_topic", required=True)

    args = parser.parse_args()

    mqtt = MQTTListener(args.mqtt_address, args.mqtt_user, args.mqtt_password, args.mqtt_client, args.mqtt_topic)
    print("running")
    mqtt.loop_forever()

