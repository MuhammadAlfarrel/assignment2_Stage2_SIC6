import network
import urequests
import dht
from machine import Pin
from time import sleep

# Konfigurasi WiFi
SSID = "Galaxy"
PASSWORD = "Alfarrel"

# Konfigurasi Ubidots
UBIDOTS_TOKEN = "BBUS-tRaXG4Ao4U87fYdF02AYYumTvKbFFP"
DEVICE_LABEL = "esp32"  # Ubah sesuai label device di Ubidots
TEMP_LABEL = "temperature"
HUMID_LABEL = "humidity"

# Konfigurasi GPIO untuk DHT11
DHT_PIN = 27  # Bisa diganti dengan GPIO lain (misalnya 4, 5, atau 16)
dht_sensor = dht.DHT11(Pin(DHT_PIN))

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
def send_to_ubidots(temp, humid):
    url = f"http://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}"
    headers = {
        "X-Auth-Token": UBIDOTS_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        TEMP_LABEL: temp,
        HUMID_LABEL: humid
    }
    
    try:
        response = urequests.post(url, json=payload, headers=headers)
        print("Response:", response.text)
        response.close()
    except Exception as e:
        print("Failed to send data:", e)

# Fungsi untuk membaca data dari DHT11 dengan retry
def read_dht():
    for _ in range(3):  # Coba maksimal 3 kali
        try:
            dht_sensor.measure()
            return dht_sensor.temperature(), dht_sensor.humidity()
        except OSError as e:
            print("Retrying sensor read...")
            sleep(2)
    return None, None  # Jika gagal terus, kembalikan None

# Mulai program
connect_wifi()

while True:
    temp, humid = read_dht()
    
    if temp is not None and humid is not None:
        print(f"Temperature: {temp}°C, Humidity: {humid}%")
        send_to_ubidots(temp, humid)
    else:
        print("Sensor gagal membaca data! Pastikan sensor tersambung dengan benar.")
    
    sleep(5)  # Tunggu 5 detik sebelum membaca ulang sensor

