from machine import Pin, ADC
from time import sleep
import config
import ds18x20
import onewire
import network
import urequests
import sys
import ubinascii

co2Pin = ADC(0)
DEVICE_ADDRESS = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()

# voltaje a 400 ppm
ZERO_POINT_VOLTAGE = 0.545   #0.740#0.511#0.606 #0.563 
V_2000 = 0.354

READ_SALMPLE_QTY = 10 #cantidad de muestreos por ciclo de medida
READ_INTERVAL = 0.05 #timepo entre muestreos por ciclo
LOG_400 = 2.602
LOG_2000 = 3.301

# voltaje a 400pp - voltaje a 2000ppm (0.511 - 0.354)
REACTION_VOLTAGE = ZERO_POINT_VOLTAGE - V_2000

def get_Read (co2Pin):
    suma = 0
    for x in range (0, READ_SALMPLE_QTY):
        suma += co2Pin.read()
        sleep(READ_INTERVAL)
    return {
        'volts':(suma/READ_SALMPLE_QTY) * 3.3/1024,
        'raw' : suma/READ_SALMPLE_QTY,
        }

def get_percentaje (v):
    return pow(10, (v - ZERO_POINT_VOLTAGE) / ( (REACTION_VOLTAGE) / (LOG_400 - LOG_2000) ) + LOG_400)

def get_temperature(sensor):
    wires = sensor.scan()
    sensor.convert_temp()
    sleep(1)
    return round(sensor.read_temp(wires[0]), 2)

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


def send_data(percentaje, volts, raw, temperature):
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
                },
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

def run():
    sensor = ds18x20.DS18X20(onewire.OneWire(Pin(config.temperature_sensor_pin)))
    while True:
        connect_wifi()
        read = get_Read(co2Pin)
        volts = round(read['volts'],3)
        print('Voltage: {}'.format(volts))
        raw = read['raw']
        print('ADC {}'.format(raw))
        percentage = round(get_percentaje(volts),1)
        print('CO2: {} ppm'.format(percentage))
        temperature = get_temperature(sensor)
        print('Temperature: {}'.format(temperature))
        try:
            send_data(percentage, volts, raw, temperature)
        except OSError as err:
            print(err)
            sleep(5)
            continue
        sleep(300)

run()
