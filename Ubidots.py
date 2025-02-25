from machine import Pin
import ujson
import network
import utime as time
import dht
import urequests as requests

# Konfigurasi WiFi dan Server
DEVICE_ID = "esp32-cihuy-neuron"
WIFI_SSID = "SUGENG FAMS"
WIFI_PASSWORD = "liantina10810"
FLASK_SERVER_IP = "192.168.1.4"  # Ganti dengan IP komputer yang menjalankan Flask
FLASK_PORT = "2008"

# Pin Setup
LED_PIN = Pin(2, Pin.OUT)
DHT_PIN = Pin(15)
PIR_PIN = Pin(19, Pin.IN)
BUZZER_PIN = Pin(18, Pin.OUT)

dht_sensor = dht.DHT11(DHT_PIN)
led = Pin(LED_PIN, Pin.OUT)
buzzer = Pin(BUZZER_PIN, Pin.OUT)

# Koneksi ke WiFi
wifi_client = network.WLAN(network.STA_IF)
wifi_client.active(True)
print("Connecting to WiFi...")
wifi_client.connect(WIFI_SSID, WIFI_PASSWORD)

while not wifi_client.isconnected():
    print("Connecting...")
    time.sleep(0.5)

print("WiFi Connected!")
print(wifi_client.ifconfig())

# Fungsi untuk membuat JSON data
def create_json_data(temperature, humidity, motion, buzzer_state):
    return ujson.dumps({
        "device_id": DEVICE_ID,
        "temp": temperature,
        "humidity": humidity,
        "pir": motion,
        "buzzer": buzzer_state,
        "type": "sensor"
    })

# Fungsi untuk mengirim data ke Flask
def send_data(temperature, humidity, motion, buzzer_status, led_status):
    url = f"http://{FLASK_SERVER_IP}:{FLASK_PORT}/data"
    headers = {"Content-Type": "application/json"}
    data = {
        "temp": temperature,
        "humidity": humidity,
        "pir": motion,
        "buzzer_status": buzzer_status,
        "led_status": led_status
    }

    try:
        response = requests.post(url, data=ujson.dumps(data), headers=headers)
        print("Data sent to Flask!")
        print("Response:", response.text)
    except Exception as e:
        print("Error sending data to Flask:", e)

# Loop utama
while True:
    try:
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        motion_detected = PIR_PIN.value()

        if motion_detected == 1:
            print("Gerakan Terdeteksi!")
            led.value(1)
            buzzer.value(1)
            buzzer_state = 1
            time.sleep(2)
        else:
            led.value(0)
            buzzer.value(0)
            buzzer_state = 0

        led_status = led.value()
        send_data(temperature, humidity, motion_detected, buzzer_state, led_status)

    except Exception as e:
        print("Error:", e)

    time.sleep(1)  # Indentasi konsisten