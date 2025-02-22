import network
import urequests
from hcsr04 import HCSR04
from time import sleep
from machine import Pin  # Tambahkan untuk kontrol LED
import dht

# Konfigurasi WiFi
SSID = "Galaxy"
PASSWORD = "Alfarrel"

# Konfigurasi Ubidots
UBIDOTS_TOKEN = "BBUS-g6JUsvQ7XKCQNRk3XFqDwHTGZoRhu5"
DEVICE_LABEL = "ubidots_sensor_assignment"  # Ubah sesuai label device di Ubidots
VARIABLE_LABEL = "jarak"
VARIABLE_WARNING = "peringatan"

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
def send_to_ubidots(value, warn):
    url = f"http://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}"
    headers = {
        "X-Auth-Token": UBIDOTS_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        VARIABLE_LABEL: value,
        VARIABLE_WARNING: warn# Gunakan angka, bukan teks!
    }
    
    try:
        response = urequests.post(url, json=payload, headers=headers)
        print("Response:", response.text)
        response.close()
    except Exception as e:
        print("Failed to send data:", e)
        
# Inisialisasi sensor & LED
sensor = HCSR04(trigger_pin=21, echo_pin=5, echo_timeout_us=10000)
led = Pin(18, Pin.OUT)

# Mulai program
connect_wifi()

while True:
    distance = sensor.distance_cm()
    
    if distance < 20:
        warn = 1  # Ganti teks dengan angka (1 = Warning)
        print("WARNING! Water Level below 20cm!")
        
        # Kirim data dengan peringatan
        send_to_ubidots(distance, warn)
        
        # Blink LED sebanyak 5 kali
        for _ in range(5):
            led.value(1)  # LED ON
            sleep(0.2)
            led.value(0)  # LED OFF
            sleep(0.2)
    else:
        warn = 0  # Jika aman, ubah warn jadi 0
        print(distance)
        send_to_ubidots(distance, warn)
    
    
    # Kirim data ke Ubidots setelah LED blinking selesai
    print(distance)

    sleep(5)  # Tunggu 5 detik sebelum membaca ulang sensor
