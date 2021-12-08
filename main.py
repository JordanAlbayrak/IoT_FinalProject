import hmac
import hashlib
import json
import schedule
import os
from dotenv import load_dotenv

from time import sleep, time
import board
import adafruit_dht

import requests
from datetime import datetime

import socketio
import ldb
from ldb import create_tables, insert_into_humidity, insert_into_temperature, get_all_humidity, get_all_temperature, purge_all

create_tables()

HOST = "https://iot-temphumid.herokuapp.com/"

sio = socketio.Client()
alive = False


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
    return { "taken_at": get_current_time(), "temperature": temperature, }


def get_humidity():
    humidity = sensor.humidity
    return { "taken_at": get_current_time(), "humidity": humidity, }


def get_temp():  # done
    response = requests.get(f'{HOST}/temperature', headers=headerHTTP)
    return response.json()


def login():
    url = f'{HOST}/login'
    payload = {"username": USERNAME, "password": PASSWORD}
    response = requests.post(url, json=payload, headers=headerHTTP)
    session_cookies = response.cookies
    return session_cookies.get("token")


def post_temperature(payload):
    # post temperature to server
    # check if url is reachable
    url = f'{HOST}/temperature'
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


def post_humidity(payload):
    # post humidity to server
    # check if url is reachable
    url = f'{HOST}/humidity'
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


@sio.on('disconnect')
def man_im_dead():
    global alive
    print("dead")
    alive = False

@sio.on('connect')
def man_im_alive():
    global alive
    print('alive')
    alive = True

    hums = get_all_humidity()
    temps = get_all_temperature()
    print(f"Posting {len(hums)} humidity readings")
    for h in hums:
        post_humidity(h)

    print(f"Posting {len(temps)} temperature readings")
    for t in temps:
       post_temperature(t)

    purge_all()



sio.connect(HOST)

def post_stats():
    global alive
    t = get_temperature()
    h = get_humidity()

    print("Posting Stats...")
    sleep(3)

    if alive:
        print("Posting to server")
        post_temperature(t)
        post_humidity(h)
    else:
        print("Saving locally")
        insert_into_temperature(t["temperature"], datetime.fromisoformat(t["taken_at"]))
        insert_into_humidity(h["humidity"], datetime.fromisoformat(h["taken_at"]))

    sleep(3)

def post_once():
    post_stats()
    return schedule.CancelJob

schedule.every(5).minutes.do(post_stats)
schedule.every().second.do(post_once)

while True:

    try:
        schedule.run_pending()
        sleep(2)

    except Exception as ex:
            print(ex)
            print("Restarting")
            sleep(30)
