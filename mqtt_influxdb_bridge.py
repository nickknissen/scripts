#!/usr/bin/env python3
import re
import json
import argparse

from typing import Any, Dict, NamedTuple

import paho.mqtt.client as mqtt

from influxdb import InfluxDBClient


class SensorData:
    measurement: str
    time: str
    fields: Dict[str, Any]
    tags: Dict[str, str]

    def __init__(self, measurement, time, value, sensor_model):
        self.measurement = measurement
        self.time = time
        self.fields = {"value": value}
        self.tags = {"model": sensor_model}

    def asdict(cls):
        return dict((key, value) for (key, value) in cls.__dict__.items())



class Influx:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database 

        self.client = InfluxDBClient(
            self.host, 8086, self.user, self.password, None
        )
        self.switch_db(self.database)

    def switch_db(self, database):
        if not any(database == x["name"] for x in self.client.get_list_database()):
            self.client.create_database(database)
        self.client.switch_database(database)

class MQTTListener:
    topic: str
    client: mqtt.Client

    def __init__(self, host, user, password, client_id, topic, influxdb_client):
        self.topic = topic
        self.client = mqtt.Client(client_id)
        self.client.username_pw_set(user, password)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(host, 1883)
        self.influxdb_client = influxdb_client

    def on_connect(self, client, userdata, flags, rc):
        self.client.subscribe(self.topic)

    def _parse_message(self, msg):
        data = json.loads(msg.payload.decode("utf-8"))

        if data["model"] == "AlectoV1 Temperature Sensor":
            return [
                SensorData("temperature", data["time"], data["temperature_C"], data["model"]),
                SensorData("battery_status", data["time"], data["battery"], data["model"]),
                SensorData("humidity", data["time"], data["humidity"], data["model"]),
            ]

        elif data["model"] == "AlectoV1 Wind Sensor":
            return [
                SensorData("wind_speed", data["time"], data["wind_speed"], data["model"]),
                SensorData("wind_gust", data["time"], data["wind_gust"], data["model"]),
                SensorData("wind_direction", data["time"], data["wind_direction"], data["model"]),
                SensorData("battery_status", data["time"], data["battery"], data["model"]),
            ]

    def on_message(self, client, userdata, msg):
        sensor_data = self._parse_message(msg)
        if sensor_data:
            json_body = [data.asdict() for data in sensor_data]

            if self.influxdb_client.write_points(json_body):
                print(f"wrote data for {sensor_data[0].tags['model']}")
            else:
                print(f"dit not write data for {sensor_data[0].tags['model']}")


    def loop_forever(self):
        self.client.loop_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="copy data from mqtt to influxdb")

    parser.add_argument("--influx-address", dest="influx_address", default="localhost")
    parser.add_argument("--influx-user", dest="influx_user", required=True)
    parser.add_argument("--influx-password", dest="influx_password", required=True)
    parser.add_argument("--influx-db", dest="influx_db", required=True)

    parser.add_argument("--mqtt-address", dest="mqtt_address", default="localhost")
    parser.add_argument("--mqtt-user", dest="mqtt_user", required=True)
    parser.add_argument(
        "--mqtt-client", dest="mqtt_client", default="MQTTInfluxDBBridge"
    )
    parser.add_argument("--mqtt-password", dest="mqtt_password", required=True)
    parser.add_argument("--mqtt-topic", dest="mqtt_topic", required=True)

    args = parser.parse_args()

    influx = Influx(args.influx_address, args.influx_user, args.influx_password, args.influx_db)
    mqtt = MQTTListener(args.mqtt_address, args.mqtt_user, args.mqtt_password, args.mqtt_client, args.mqtt_topic, influx.client)
    print("running")
    mqtt.loop_forever()

