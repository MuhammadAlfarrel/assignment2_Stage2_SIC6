import network
import urequests
from modules.hcsr04 import HCSR04
from time import sleep
from machine import Pin
import dht
import json

SSID = "akanesan"
PASSWORD = "12345678"

UBIDOTS_TOKEN = "BBUS-g6JUsvQ7XKCQNRk3XFqDwHTGZoRhu5"
DEVICE_LABEL = "ubidots_sensor_assignment"
VARIABLE_LABEL = "jarak"
VARIABLE_WARNING = "peringatan"
TEMP_LABEL = "temperature"
HUMID_LABEL = "humidity"

SERVER_IP = "127.0.0.1"
SERVER_PORT = "5000"
SERVER_URL = f"http://{SERVER_IP}:{SERVER_PORT}/sensor"

DHT_PIN = 4
dht_sensor = dht.DHT11(Pin(DHT_PIN))

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    while not wlan.isconnected():
        print("Connecting to WiFi...")
        sleep(1)

    print("Connected to WiFi:", wlan.ifconfig())

def send_to_ubidots(value, warn, temp, humid):
    url = f"http://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}"
    headers = {"X-Auth-Token": UBIDOTS_TOKEN, "Content-Type": "application/json"}
    payload = {
        VARIABLE_LABEL: value,
        VARIABLE_WARNING: warn,
        TEMP_LABEL: temp,
        HUMID_LABEL: humid
    }
    try:
        response = urequests.post(url, json=payload, headers=headers)
        print("Ubidots Response:", response.text)
        response.close()
    except Exception as e:
        print("Failed to send data to Ubidots:", e)

def send_to_server(distance, warn, temp, humid):
    headers = {"Content-Type": "application/json"}
    payload = {
        "distance": distance,
        "warning": warn,
        "temperature": temp,
        "humidity": humid
    }
    try:
        response = urequests.post(SERVER_URL, json=payload, headers=headers)
        print("Server Response:", response.status_code, response.text)
        response.close()
    except Exception as e:
        print("Failed to send data to server:", e)

def read_dht():
    for _ in range(3):
        try:
            dht_sensor.measure()
            return dht_sensor.temperature(), dht_sensor.humidity()
        except OSError as e:
            print("Retrying sensor read...")
            sleep(2)
    return None, None

sensor = HCSR04(trigger_pin=21, echo_pin=5, echo_timeout_us=10000)

connect_wifi()

while True:
    distance = sensor.distance_cm()
    temp, humid = read_dht()

    if temp is not None and humid is not None:
        print(f"Temperature: {temp}°C, Humidity: {humid}%")
        warn = 1 if distance < 20 else 0
        if distance < 20:
            print("WARNING! Water Level below 20cm!")
        send_to_ubidots(distance, warn, temp, humid)
        send_to_server(distance, warn, temp, humid)
    else:
        print("Sensor gagal membaca data! Pastikan sensor tersambung dengan benar.")

    print(distance)
    sleep(3)
