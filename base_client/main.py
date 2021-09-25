"""
The main Device's Logic. 
Here we can read inputs, calculate values, send data to the API using utils.py module, and more.
"""
import config
from time import sleep
from utils import Connection, Sender, Sleeper
from machine import Pin # import evrery you need to work with ESP8266 based board

HEADER: dict ={'Content-type':'application/json'}
connection = Connection(config.WIFI_SSID,config.WIFI_PASSWORD)
sleeper = Sleeper(config.SLEEP_INTERVAL)
sender = Sender(config.API_URL,HEADER)

import dht
DHT_PIN = 5
sensor = dht.DHT22(Pin(DHT_PIN))

def create_json():
    return {
        'unic_id': Connection.get_mac(),
        'values':[
            {
                "value": read_temp(),
                "alias": "temperatura",
            },
            {
                "value": read_hum(),
                "alias": "humedad"
            }
        ]
    }

def read_temp():
    sensor.measure()
    return sensor.temperature()

def read_hum():
    sensor.measure
    return sensor.humidity()

def send_data(data):
    response = object
    try:
       response = sender.send_data(data)
    except Exception as e:
        response = None
    finally:
        sleep(5)
        return response

def run():
    while True:
        print('running')
        data = create_json()
        print(data)
        connection.connect()
        response = send_data(data)
        print(response)
        if response is not None:
            print(response.text)
            sleeper.deepSleep()

run()