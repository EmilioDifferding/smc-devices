"""
Class Colection with all the common functionalities to suspend the device, connect to wi-fi and send data to the SMC-API
"""
import network
from time import sleep
import ubinascii
import machine 
import urequests

class Sleeper():
    def __init__(self, sleepInterval: int) -> None:
        self.sleepInterval = sleepInterval * 60000

    def deepSleep(self) -> None:
        """
        suspend the device and set the RTC alarm based on the time given in minutes
        """
        rtc = machine.RTC()
        rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
        rtc.alarm(rtc.ALARM0, self.sleepInterval)
        machine.deepsleep()

class Connection():
    def __init__(self, ssid: str, password: str) -> None:
        self.ssid = ssid
        self.password = password
    
    
    def connect(self) -> None:
        ap_if = network.WLAN(network.AP_IF)
        ap_if.active(False)
        sta_if = network.WLAN(network.STA_IF)
        if not sta_if.isconnected():
            sta_if.active(True)
            sta_if.connect(self.ssid, self.password)
            while not sta_if.isconnected():
                sleep(1)
        print('connected...')
    
    @staticmethod
    def get_mac() -> str:
        return ubinascii.hexlify(network.WLAN().config('mac'),':').decode()

class Sender():
    def __init__(self, url: str, headers: str) -> None:
        self.url = url
        self.headers = headers
    
    def send_data(self, data: dict) -> object:
        request = urequests.post(
            self.url,
            json = data,
            headers = self.headers
        )
        return request
