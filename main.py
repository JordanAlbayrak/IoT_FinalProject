import hmac
import hashlib
import json
import sys
import schedule
import os
from dotenv import load_dotenv

import requests
from time import sleep, time
import board
import adafruit_dht

import requests
from datetime import datetime

load_dotenv()
API_KEY = os.environ.get('SECRET')
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")

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


def login():
    url = 'https://iot-temphumid.herokuapp.com/login'
    payload = {"username": USERNAME, "password": PASSWORD}
    response = requests.post(url, json=payload, headers=headerHTTP)
    session_cookies = response.cookies
    return session_cookies.get("token")



def post_temperature():
    # post temperature to server
    # check if url is reachable
    url = 'https://iot-temphumid.herokuapp.com/temperature'
    payload = {'taken_at': get_current_time(), 'temperature': get_temperature(), }
    response = requests.Request('POST', url, json=payload, headers=headerHTTP, cookies={"token": login()})
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
    response = requests.Request('POST', url, json=payload, headers=headerHTTP, cookies={"token": login()})
    prepared = response.prepare()
    signature = hmac.new(API_KEY.encode(), json.dumps(payload).encode(),
                         hashlib.sha256).hexdigest()
    prepared.headers['X-Auth-Signature'] = signature
    # print(json.dumps(payload))
    # print(signature)
    with requests.Session() as session:
        response = session.send(prepared)
    # print(response.text)


def post_stats():
    print("Posting Stats...")
    sleep(3)
    post_temperature()
    post_humidity()
    sleep(3)

schedule.every(440).minutes.do(login)
schedule.every(5).minutes.do(post_stats)


while True:



    try:
        # schedule.run_pending()
        login()
        sleep(3)
        post_stats()
        sleep(3)

    except Exception as ex:
        if ex is BufferError:
            print("Buffer Error")
            quit()
        else:
            print(ex)
            print("Restarting")
            sleep(30)
