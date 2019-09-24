#!/usr/bin/env python3
import requests
import json
import argparse


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

def fetch_data(token, meter, start="2019-09-22", end="2019-09-24", aggregation="Hour"):
    url = f"https://msn-api.seas-nve.dk/api/v1.0/profile/consumption/?meteringpoints={meter}&start={start}&end={end}&aggr={aggregation}"

    headers = {
        "Authorization": f"Bearer {token}",
    }

    response = requests.get(url, headers=headers)

    print(response.json())



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch data from seas and store it in influxdb')
    parser.add_argument('--user', dest='user', required=True)
    parser.add_argument('--pass', dest='password', required=True)
    parser.add_argument('--meter', dest='meter', required=True)
    args = parser.parse_args()

    token = login(args.user, args.password)

    data = fetch_data(token, args.meter)

    
    
