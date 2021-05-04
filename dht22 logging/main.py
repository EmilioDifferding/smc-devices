from machine import Pin, RTC
from time import sleep
import config
import network
import urequests
import ubinascii
import sys
import dht

sensor = dht.DHT22(Pin(5))

#get the MAC Address used to validate in the API
DEVICE_ADDRESS = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
sensor.measure()
humedad = sensor.humidity()
temperatura= sensor.temperature()
def get_temp():
    sensor.measure()
    return sensor.temperature()
def get_hum():
    sensor.measure()
    return sensor.humidity()
def send_data():
    print(config.API_URL)
    print(DEVICE_ADDRESS)
    json = {
        "unic_id": str(DEVICE_ADDRESS),
        "values":[
            {
                "value": get_temp(),
                "alias": "temperatura"
            },
            {
                "value": get_hum(),
                "alias": "humedad"
            }
        ]
    }
    print(json)
    req = urequests.post(
        'http://smc-fcal.duckdns.org/api/store-data',
        json = json,
        headers={'Content-Type': 'application/json'}
    )
    print("STATUS CODE")
    print(req.status_code)
    print(req.text)
    if req.status_code < 400:
        print('Webhook invoked')
    else:
        print('Webhook failed')
        raise RuntimeError('Webhook failed')

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

def deepsleep():
    """
    Routine for suspend the device and wake up after DSL_INTERVAL
    """
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    rtc.alarm(rtc.ALARM0, config.SLEEP_INTERVAL * 1000)
    machine.deepsleep()

def run():
    while True:
        try:
            connect_wifi()
            print('running')
            try:
                send_data()
                print('going to sleep zzzz...')
                # deepsleep()
            except OSError as err:
                print (err)
                continue
        except Exception as exc:
            sys.print_exception(exc)
        sleep(config.SLEEP_INTERVAL)

run()