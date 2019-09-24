#!/usr/bin/env python3
import re
import json

from typing import Dict, NamedTuple, Any

import paho.mqtt.client as mqtt
import argparse

from influxdb import InfluxDBClient


parser = argparse.ArgumentParser(description='copy data from mqtt to influxdb')
parser.add_argument('--influx-address', dest='influx_address', default="localhost")
parser.add_argument('--influx-user', dest='influx_user', required=True)
parser.add_argument('--influx-password', dest='influx_password', required=True)
parser.add_argument('--influx-db', dest='influx_db', required=True)


parser.add_argument('--mqtt-address', dest='mqtt_address', default="localhost")
parser.add_argument('--mqtt-user', dest='mqtt_user', required=True)
parser.add_argument('--mqtt-client', dest='mqtt_client', default="MQTTInfluxDBBridge")
parser.add_argument('--mqtt-password', dest='mqtt_password', required=True)
parser.add_argument('--mqtt-topic', dest='mqtt_topic', required=True)

args = parser.parse_args()

influxdb_client = InfluxDBClient(
    args.influx_address, 8086, args.influx_user, args.influx_password, None
)


class SensorData(NamedTuple):
    measurement: str
    time: str
    fields: Dict[str, Any]
    tags: Dict[str, str]




def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print("Connected with result code " + str(rc))
    client.subscribe(args.mqtt_topic)


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    #print(msg.topic + " " + str(msg.payload))
    sensor_data = _parse_mqtt_message(msg.topic, msg.payload.decode("utf-8"))
    if sensor_data:
        _send_sensor_data_to_influxdb(sensor_data)


def _parse_mqtt_message(topic, payload):
    data = json.loads(payload)
    print("")
    print("mqtt data", data)
    sensor_data = []
    if data["model"] == "AlectoV1 Temperature Sensor":
        print("mqtt data modek AlectoV1 Temperature Sensor")
        sensor_data = [
            SensorData(
                "temperature",
                data["time"],
                data["temperature_C"],
                {"value": data["temperature_C"]},
                {"model": data["model"]},
            ),
            SensorData(
                "battery_status",
                data["time"],
                {"value": data["battery"]},
                {"model": data["model"]},
            ),
            SensorData(
                "humidity", 
                data["time"], 
                {"value": data["humidity"]}, 
                {"model": data["model"]}
            ),
        ]

    elif data["model"] == "AlectoV1 Wind Sensor":
        sensor_data = [
            SensorData(
                "wind_speed", 
                data["time"], 
                {"value": data["wind_speed"]}, 
                {"model": data["model"]}
            ),
            SensorData(
                "wind_gust", 
                data["time"], 
                {"value": data["wind_gust"]}, 
                {"model": data["model"]}
            ),
            SensorData(
                "wind_direction",
                data["time"],
                {"value": data["wind_direction"]},
                {"model": data["model"]},
            ),
            SensorData(
                "battery_status",
                data["time"],
                {"value": data["battery"]},
                {"model": data["model"]},
            ),
        ]

    print(sensor_data)
    return sensor_data

def _send_sensor_data_to_influxdb(sensor_data):
    print("sensor_data", sensor_data)
    json_body = [
        data._asdict() for data in sensor_data
    ]

    if not json_body:
        return None

    written = influxdb_client.write_points(json_body)

    if written:
        print(f"wrote data for {sensor_data[0].tags['model']}")

def _init_influxdb_database():
    databases = influxdb_client.get_list_database()
    if len(list(filter(lambda x: x["name"] == args.influx_db, databases))) == 0:
        influxdb_client.create_database(args.influx_db)
    influxdb_client.switch_database(args.influx_db)


def main():
    _init_influxdb_database()

    mqtt_client = mqtt.Client(args.mqtt_client)
    mqtt_client.username_pw_set(args.mqtt_user, args.mqtt_password)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(args.mqtt_address, 1883)
    mqtt_client.loop_forever()


if __name__ == "__main__":
    print("MQTT to InfluxDB bridge")
    main()

