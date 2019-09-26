#!/usr/bin/env python3
from typing import Any, Dict, NamedTuple
import requests
import json
import argparse
import calendar
from datetime import datetime

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

def login(username, password):

    headers = {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
        'Content-Type': 'application/json;charset=UTF-8',
    }

    data = '{"username":"%s","password":"%s"}' % (username, password)

    response = requests.post('https://msn-api.seas-nve.dk/api//v1.0/auth', headers=headers, data=data)
    json_response = response.json()

    return json_response["accessToken"]

def fetch_data(token, meter, start=None, end=None, aggregation="Hour"):
    """
    There is a limit of 32 days of data with hour aggregation
    """

    if not start:
        start = datetime.today().date().replace(day=1)
    else:
        start = datetime.strptime(start, '%Y-%m-%d') 

    if not end:
        year = datetime.today().year
        (_, last_day_of_month) = calendar.monthrange(year, start.month)
        end = '{}-{:02d}-{:02d}'.format(year, start.month, last_day_of_month)


    start = start.strftime('%Y-%m-%d') 

    print(f"fetching date from {start} to {end}")

    url = f"https://msn-api.seas-nve.dk/api/v1.0/profile/consumption/?meteringpoints={meter}&start={start}&end={end}&aggr={aggregation}"

    headers = {
        "Authorization": f"Bearer {token}",
    }

    response = requests.get(url, headers=headers)

    return response.json()

def transform_data(data):
    return [dict(measurement="power_consumption", time=item["end"], fields=dict(value=item["value"]))
            for item in data["meteringPoints"][0]["values"]]

def fetch_and_write(influx, meter, date_from=None, date_to=None):
    data = fetch_data(token, meter, date_from, date_to)

    preped_data = transform_data(data)
    influx.write_points(preped_data)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch data from seas and store it in influxdb')
    parser.add_argument('--user', dest='user', required=True)
    parser.add_argument('--pass', dest='password', required=True)
    parser.add_argument('--meter', dest='meter', required=True)
    parser.add_argument('--influx-url', dest='influx_url', required=True)
    parser.add_argument('--from', dest='date_from', default=None)
    parser.add_argument('--to', dest='date_to', default=None)
    parser.add_argument('--all', dest='all', default=False, action="store_true")
    args = parser.parse_args()

    token = login(args.user, args.password)
    influx = InfluxDBClient.from_dsn(args.influx_url)
    
    if args.all:
        for year in range(2016, 2020):
            for month in range(1, 13):
                date = '{}-{:02d}-01'.format(year, month)

                fetch_and_write(influx, args.meter, date)
    else:
        fetch_and_write(influx, args.meter, args.date_from, args.date_to)
