#!/usr/bin/env python3
import os
import sys
import json
import time
import argparse
import subprocess

import paho.mqtt.client as mqtt

rtl433_proc = subprocess.Popen(
    "/usr/local/bin/rtl_433 -F json -M level".split(),
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    universal_newlines=True,
)


if __name__ == "main":
    parser = argparse.ArgumentParser(description="Move data from rtl_433 to mqtt")
    parser.add_argument("--mqtt-address", dest="mqtt_address", default="localhost")
    parser.add_argument("--mqtt-port", dest="mqtt_port", default=1883)
    parser.add_argument("--mqtt-qos", dest="mqtt_qos", default=0)
    parser.add_argument("--mqtt-user", dest="mqtt_user", required=True)
    parser.add_argument("--mqtt-password", dest="mqtt_password", required=True)
    parser.add_argument("--mqtt-client", dest="mqtt_client", default="rtl_433")
    parser.add_argument("--mqtt-topic", dest="mqtt_topic", default="sensors/rtl_433")

    args = parser.parse_args()

    mqttc = mqtt.Client(client_id="rtl_443")
    mqttc.username_pw_set(args.mqtt_user, password=args.mqtt_password)
    mqttc.connect(args.mqtt_address, args.mqtt_port, 60)

    mqttc.loop_start()

    """ Example of output
    {
        "time" : "2019-09-25 13:51:11",
        "model" : "AlectoV1 Wind Sensor",
        "id" : 33,
        "channel" : 1,
        "battery" : "OK",
        "wind_speed" : 2.200,
        "wind_gust" : 2.400,
        "wind_direction" : 225,
        "mic" : "CHECKSUM",
        "mod" : "ASK",
        "freq" : 433.843,
        "rssi" : -0.099,
        "snr" : 10.584
    }
    """
    while True:
        for line in iter(rtl433_proc.stdout.readline, "\n"):
            try:
                json_dict = json.loads(line)
            except json.decoder.JSONDecodeError:
                continue

            mqttc.publish(args.mqtt_topic, payload=line, qos=args.mqtt_qos)

            subtopic = json_dict.pop("model")

            for key, value in json_dict.items():
                mqttc.publish(
                    args.mqtt_topic + "/" + subtopic + "/" + key,
                    payload=value,
                    qos=args.mqtt_qos,
                )

