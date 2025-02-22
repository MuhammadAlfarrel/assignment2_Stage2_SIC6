import network
import urequests
from hcsr04 import HCSR04
from time import sleep
from machine import Pin

# Konfigurasi WiFi
SSID = "Galaxy"
PASSWORD = "Alfarrel"

# Konfigurasi Ubidots
UBIDOTS_TOKEN = "BBUS-g6JUsvQ7XKCQNRk3XFqDwHTGZoRhu5"
DEVICE_LABEL = "ubidots_sensor_assignment"  # Ubah sesuai label device di Ubidots
VARIABLE_LABEL = "jarak"

# Koneksi WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    
    while not wlan.isconnected():
        print("Connecting to WiFi...")
        sleep(1)
    
    print("Connected to WiFi:", wlan.ifconfig())

# Fungsi untuk mengirim data ke Ubidots
def send_to_ubidots(value):
    url = f"http://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}"
    headers = {
        "X-Auth-Token": UBIDOTS_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {VARIABLE_LABEL: value}
    
    try:
        response = urequests.post(url, json=payload, headers=headers)
        print("Response:", response.text)
        response.close()
    except Exception as e:
        print("Failed to send data:", e)

# Inisialisasi sensor
sensor = HCSR04(trigger_pin=12, echo_pin=14, echo_timeout_us=10000)

# Mulai program
connect_wifi()

while True:
    distance = sensor.distance_cm()
    print("Distance:", distance, "cm")
    send_to_ubidots(distance)  # Kirim data ke Ubidots
    sleep(1)  # Kirim data setiap 5 detik

