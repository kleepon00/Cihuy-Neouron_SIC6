from machine import Pin, ADC
import ujson
import network
import utime as time
import dht
import urequests as requests


DEVICE_ID = "esp32-cihuy-neuron"
WIFI_SSID = "SUGENG FAMS"
WIFI_PASSWORD = "liantina10810"
TOKEN = "BBUS-cRGUl6aSBHHiw5ASS9JOhoIQZCQOd1"

LED_PIN = Pin(4, Pin.OUT)
DHT_PIN = Pin(2)
PIR_PIN = Pin(19, Pin.IN)
BUZZER_PIN = Pin(18, Pin.OUT)

dht_sensor = dht.DHT11(DHT_PIN)
led = Pin(LED_PIN, Pin.OUT)
buzzer = Pin(BUZZER_PIN, Pin.OUT)

wifi_client = network.WLAN(network.STA_IF)
wifi_client.active(True)
print("Connecting device to WiFi")
wifi_client.connect(WIFI_SSID, WIFI_PASSWORD)

while not wifi_client.isconnected():
    print("Connecting")
    time.sleep(0.1)
    
print("WiFi Connected!")
print(wifi_client.ifconfig())

def create_json_data(temperature, humidity,pir,buzzer_state):
    data = ujson.dumps({
        "device_id": DEVICE_ID,
        "temp": temperature,
        "humidity": humidity,
        "pir": pir,
        "buzzer": buzzer_state,
        "type": "sensor"
    })
    return data

def send_data(temperature, humidity,pir,buzzer_status,led_status):
    url = "http://industrial.api.ubidots.com/api/v1.6/devices/" + DEVICE_ID
    headers = {"Content-Type": "application/json", "X-Auth-Token": TOKEN}
    data = {
        "temp": temperature,
        "humidity": humidity,
        "pir": pir,
        "buzzer_status": buzzer_status,
        "led_status": led_status
    }
    
    try :
        response = requests.post(url, json=data, headers=headers)
        print("Data Send!")
        print("Response:", response.text)
    except Exception as e:
        print("Error sending data:", e)	

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
            buzzer.value(0)
        else:
            led.value(0)
            buzzer_state = 0
            
        send_data(temperature, humidity, motion_detected, buzzer_state)
    
    except Exception as e:
        print("Error:", e)
        
    time.sleep(2)
