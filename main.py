import hmac
import hashlib
import json
import requests
from time import sleep, time
import board
import adafruit_dht

import requests
from datetime import datetime

sensor = adafruit_dht.DHT22(board.D17)
headerHTTP = {'Content-Type': 'application/json'}


def get_current_time():
    return datetime.now().isoformat()


def get_temperature():
    temperature = sensor.temperature
    return temperature


def get_humidity():
    humidity = sensor.humidity
    return humidity


def get_temp():  # done
    response = requests.get('https://iot-temphumid.herokuapp.com/temperature', headers=headerHTTP)
    return response.json()


def post_temperature():
    # post temperature to server
    # check if url is reachable
    url = 'https://iot-temphumid.herokuapp.com/temperature'
    payload = {'taken_at': get_current_time(), 'temperature': get_temperature(), }
    response = requests.Request('POST', url, json=payload, headers=headerHTTP)
    prepared = response.prepare()
    signature = hmac.new('d66e56d4c0d6184396d1d99614183850b7a9cd79'.encode(), json.dumps(payload).encode(),
                         hashlib.sha256).hexdigest()
    prepared.headers['X-Auth-Signature'] = signature
    # print(json.dumps(payload))
    # print(signature)
    with requests.Session() as session:
        response = session.send(prepared)
    # print(response.text)


def post_humidity():
    # post humidity to server
    # check if url is reachable
    url = 'https://iot-temphumid.herokuapp.com/humidity'
    payload = {'taken_at': get_current_time(), 'humidity': get_humidity()}
    response = requests.Request('POST', url, json=payload, headers=headerHTTP)
    prepared = response.prepare()
    signature = hmac.new('d66e56d4c0d6184396d1d99614183850b7a9cd79'.encode(), json.dumps(payload).encode(),
                         hashlib.sha256).hexdigest()
    prepared.headers['X-Auth-Signature'] = signature
    # print(json.dumps(payload))
    # print(signature)
    with requests.Session() as session:
        response = session.send(prepared)
    # print(response.text)


def post_stats():
    post_temperature()
    post_humidity()


try:
    while 1:
        print("Posting Stats...")
        post_temperature()
        post_humidity()
        sleep(1200)

except:
    print("Unknown Error")
    print("Exiting")
    exit()
