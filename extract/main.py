from machine import Pin, ADC, RTC
from time import sleep
import config
import network
import urequests
import ubinascii
import sys
import ujson

#get the MAC Address used to validate in the API
DEVICE_ADDRESS = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()

battery_pin = ADC(config.BATTERY)
voltaje_pin = Pin(config.VOLTAJE_STATUS, Pin.IN)

def send_data():
    print(config.API_URL)
    req = urequests.post(
        config.API_URL,
        json = {
            "unic_id": str(DEVICE_ADDRESS),
            "values":[
                {
                    "value": get_battery_status(),
                    "alias": "bateria"
                },
                {
                    "value": get_voltaje_status(),
                    "alias": "estado"
                }
            ]
    })
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

def get_battery_status():
    """Return the aproximate value of battery load TODO:(The formula need improvements)"""
    raw_value = battery_pin.read()
    return (round(((raw_value - 806) * 100) / 218))

def get_voltaje_status():
    return 1 if voltaje_pin.value() else 0

def deepsleep():
    """
    Routine for suspend the device and wake up after DSL_INTERVAL
    """
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    rtc.alarm(rtc.ALARM0, config.SLEEP_INTERVAL * 1000)
    machine.deepsleep()


def run():
    try:
        connect_wifi()
        print('running')
        send_data()
        print('going to sleep zzzz...')
        deepsleep()
    except Exception as exc:
        sys.print_exception(exc)
        sleep(10)
    

run()