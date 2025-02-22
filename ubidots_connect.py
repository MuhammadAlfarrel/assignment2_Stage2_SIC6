import network
import urequests
from hcsr04 import HCSR04
from time import sleep
from machine import Pin  # Tambahkan untuk kontrol LED
import dht

# Konfigurasi WiFi
SSID = "akanesan"
PASSWORD = "12345678"

# Konfigurasi Ubidots
UBIDOTS_TOKEN = "BBUS-g6JUsvQ7XKCQNRk3XFqDwHTGZoRhu5"
DEVICE_LABEL = "ubidots_sensor_assignment"  # Ubah sesuai label device di Ubidots
VARIABLE_LABEL = "jarak"
VARIABLE_WARNING = "peringatan"
TEMP_LABEL = "temperature"
HUMID_LABEL = "humidity"

DHT_PIN = 4  # Bisa diganti dengan GPIO lain (misalnya 4, 5, atau 16)
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
def send_to_ubidots(value, warn, temp, humid):
    url = f"http://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}"
    headers = {
        "X-Auth-Token": UBIDOTS_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        VARIABLE_LABEL: value,
        VARIABLE_WARNING: warn,
        TEMP_LABEL: temp,
        HUMID_LABEL: humid
    }
    
    try:
        response = urequests.post(url, json=payload, headers=headers)
        print("Response:", response.text)
        response.close()
    except Exception as e:
        print("Failed to send data:", e)

def read_dht():
    for _ in range(3):  # Coba maksimal 3 kali
        try:
            dht_sensor.measure()
            return dht_sensor.temperature(), dht_sensor.humidity()
        except OSError as e:
            print("Retrying sensor read...")
            sleep(2)
    return None, None  # Jika gagal terus, kembalikan None

        
# Inisialisasi sensor & LED
sensor = HCSR04(trigger_pin=21, echo_pin=5, echo_timeout_us=10000)
led = Pin(18, Pin.OUT)

# Mulai program
connect_wifi()

while True:
    distance = sensor.distance_cm()
    temp, humid = read_dht()
    
    if temp is not None and humid is not None:
        print(f"Temperature: {temp}°C, Humidity: {humid}%")
        if distance < 20:
            warn = 1  # Ganti teks dengan angka (1 = Warning)
            print("WARNING! Water Level below 20cm!")
            
            # Kirim data dengan peringatan
            send_to_ubidots(distance, warn,temp, humid)
            
            # Blink LED sebanyak 5 kali
            for _ in range(5):
                led.value(1)  # LED ON
                sleep(0.2)
                led.value(0)  # LED OFF
                sleep(0.2)
        else:
            warn = 0  # Jika aman, ubah warn jadi 0
            send_to_ubidots(distance, warn, temp, humid)
    else:
        print("Sensor gagal membaca data! Pastikan sensor tersambung dengan benar.")
    
    
    # Kirim data ke Ubidots setelah LED blinking selesai
    print(distance)

    sleep(5)  # Tunggu 5 detik sebelum membaca ulang sensor
