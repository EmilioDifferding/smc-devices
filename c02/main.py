from machine import Pin, ADC
from time import sleep
import config
import network
import urequests
import sys
import ubinascii

co2Pin = ADC(0)
DEVICE_ADDRESS = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()

# voltaje a 400 ppm
ZERO_POINT_VOLTAGE = 0.889

# voltaje a 400pp - voltaje a 6000ppm (0.889 - 0.645)
REACTION_VOLTAGE = 0.244

READ_SALMPLE_QTY = 10 #cantidad de muestreos por ciclo de medida
READ_INTERVAL = 0.05 #timepo entre muestreos por ciclo

CO2Curve = [
    2.602, 
    ZERO_POINT_VOLTAGE, 
    (REACTION_VOLTAGE/(2.602 - 3.778))
]

def get_Read (co2Pin):
    suma = 0
    for x in range (0, READ_SALMPLE_QTY):
        suma += co2Pin.read()
        sleep(READ_INTERVAL)
    return {
        'volts':(suma/READ_SALMPLE_QTY) * 3.3/1024,
        'raw' : suma/READ_SALMPLE_QTY,
        }

def get_percentaje (v, CO2Curve):
    return pow(10, (v - ZERO_POINT_VOLTAGE) / ( (ZERO_POINT_VOLTAGE-0.645) / (-1.176) ) + CO2Curve[0])

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


def send_data(percentaje, volts, raw):
    json={
            "unic_id" : str(DEVICE_ADDRESS),
            "values" : [
                {
                    'value': percentaje,
                    'alias': 'CO2'
                },
                {
                    'value': raw,
                    'alias': 'ADC'
                },
                {
                    'value': volts,
                    'alias': 'volts'
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

def run():
    while True:
        connect_wifi()
        read = get_Read(co2Pin)
        volts = round(read['volts'],3)
        print('Voltage: {}'.format(volts))
        raw = read['raw']
        print('ADC {}'.format(raw))
        percentage = round(get_percentaje(volts, CO2Curve),3)
        print('CO2: {} ppm'.format(percentage))
        try:
            send_data(percentage, volts, raw)
        except OSError as err:
            print(err)
            sleep(5)
            continue
        sleep(300)

run()