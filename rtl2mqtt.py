#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import subprocess
import sys
import time
import paho.mqtt.client as mqtt
import os
import json
import argparse

parser = argparse.ArgumentParser(description='Move data from rtl_433 to mqtt')
parser.add_argument('--mqtt-address', dest='mqtt_address', default="localhost")
parser.add_argument('--mqtt-port', dest='mqtt_port', default=1883)
parser.add_argument('--mqtt-qos', dest='mqtt_qos', default=0)
parser.add_argument('--mqtt-user', dest='mqtt_user', required=True)
parser.add_argument('--mqtt-password', dest='mqtt_password', required=True)
parser.add_argument('--mqtt-client', dest='mqtt_client', default="rtl_433")
parser.add_argument('--mqtt-topic', dest='mqtt_topic', default="sensors/rtl_433")

args = parser.parse_args()



rtl_433_cmd = "/usr/local/bin/rtl_433 -F json -M level" # linux

# Define MQTT event callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")

def on_message(client, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def on_publish(client, obj, mid):
    print("mid: " + str(mid))

def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(client, obj, level, string):
    print(obj, level, string)

# Setup MQTT connection

mqttc = mqtt.Client(client_id="rtl_443")
# Assign event callbacks
#mqttc.on_message = on_message
mqttc.on_connect = on_connect
#mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
mqttc.on_disconnect = on_disconnect

# Uncomment to enable debug messages
mqttc.on_log = on_log
# Uncomment the next line if your MQTT server requires authentication
mqttc.username_pw_set(args.mqtt_user, password=args.mqtt_password)
mqttc.connect(args.mqtt_address, args.mqtt_port, 60)

mqttc.loop_start()

# Start RTL433 listener
rtl433_proc = subprocess.Popen(rtl_433_cmd.split(),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True)


while True:
    for line in iter(rtl433_proc.stdout.readline, '\n'):
        if "time" in line:
            mqttc.publish(args.mqtt_topic, payload=line,qos=args.mqtt_qos)
            json_dict = json.loads(line)
            for item in json_dict:
                value = json_dict[item]
                if "model" in item:
                    subtopic=value

            for item in json_dict:
                value = json_dict[item]
                if not "model" in item:
                    mqttc.publish(args.mqtt_topic+"/"+subtopic+"/"+item, payload=value,qos=args.mqtt_qos)
