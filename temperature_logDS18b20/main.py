import config
import onewire
import ds18x20
from time import sleep
from machine import Pin
import network
import urequests
import sys
import ubinascii


DEVICE_ADDRESS = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()

def connect_wifi():
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('Connecting to WiFi...'+ config.WIFI_SSID)
        sta_if.active(True)
        sta_if.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        while not sta_if.isconnected():  #and countertrays < 10
            sleep(1)
    print('Network config:', sta_if.ifconfig())

def send_data(temperature):
    json={
            "unic_id" : str(DEVICE_ADDRESS),
            "values" : [
                {
                    'value': temperature,
                    'alias': 'temperatura'
                }
            ]
        }
    print(json)
    req = urequests.post(
        config.API_URL,
        json = json,
        headers = {'Content-Type': 'application/json'}
    )
    print("STATUS CODE")
    print(req.status_code)
    print(req.text)
    if req.status_code < 400:
        print('Webhook invoked')
    else:
        print('Webhook failed')
        raise RuntimeError('Webhook failed')


def get_read(sensor):
    wires = sensor.scan()
    sensor.convert_temp()
    sleep(1)
    return round(sensor.read_temp(wires[0]),2)


def run():
    sensor = ds18x20.DS18X20(onewire.OneWire(Pin(config.sensor_pin)))
    while True:
        connect_wifi()
        temperature = get_read(sensor)
        try:
            send_data(temperature)
        except OSError as err:
            print(err)
            sleep(5)
            continue
        sleep(300)

run()