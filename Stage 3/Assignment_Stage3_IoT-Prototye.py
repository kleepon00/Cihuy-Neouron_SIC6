import time
import network
import urequests
from machine import Pin, ADC, PWM
import dht

# KONFIGURASI UBIDOTS
UBIDOTS_TOKEN = "BBUS-3QZt39CQQv31S8IiKsGcc2Uv8pJehX"
DEVICE_LABEL = "esp32_cihuy_neuron"
UBIDOTS_URL = "http://industrial.api.ubidots.com/api/v1.6/devices/" + DEVICE_LABEL

# KONFIGURASI WIFI
SSID = "SUGENG FAMS"
PASSWORD = "liantina10810"

# INISIALISASI WIFI
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
    print("Connected to WiFi:", wlan.ifconfig())

# INISIALISASI SENSOR DAN OUTPUT
dht_sensor = dht.DHT11(Pin(15))  
ldr = ADC(Pin(34))               
ldr.atten(ADC.ATTN_11DB)

# LED suhu
led_hijau = Pin(13, Pin.OUT)
led_kuning = Pin(12, Pin.OUT)
led_merah = Pin(14, Pin.OUT)

# LED LDR
led_ldr_hijau = Pin(27, Pin.OUT)
led_ldr_merah = Pin(26, Pin.OUT)

# Buzzer
buzzer = PWM(Pin(25))
buzzer.freq(1000)
buzzer.duty(0)


# COUNTER MONITORING 
led_kuning_count = 0
led_merah_count = 0
led_hijau_count = 0
ldr_redup_count = 0

# LED SUHU 
def led_suhu(temp):
    global led_kuning_count, led_merah_count,led_hijau_count

    if 24 <= temp <= 30:
        led_hijau.on()
        led_kuning.off()
        led_merah.off()
        buzzer.duty(0)
        led_hijau_count += 1
    elif 20 <= temp < 24 or 30 < temp <= 34:
        led_kuning.on()
        led_hijau.off()
        led_merah.off()
        buzzer.duty(0)
        led_kuning_count += 1
    else:
        led_merah.on()
        led_hijau.off()
        led_kuning.off()
        buzzer.duty(512)
        led_merah_count += 1

# FUNGSI DETEKSI CAHAYA
def deteksi_cahaya():
    global ldr_redup_count
    ldr_value = ldr.read()

    if ldr_value < 1000:
        led_ldr_merah.on()
        led_ldr_hijau.off()
        ldr_redup_count += 1
    else:
        led_ldr_merah.off()
        led_ldr_hijau.on()
    return ldr_value

# FUNGSI KIRIM DATA KE UBIDOTS
def kirim_data(temp, hum, light):
    data = {
        "temperature": temp,
        "humidity": hum,
        "light": light,
        "led_kuning_count": led_kuning_count,
        "led_merah_count": led_merah_count,
        "led_hijau_count": led_hijau_count,
        "redup_count": ldr_redup_count
    }

    headers = {
        "X-Auth-Token": UBIDOTS_TOKEN,
        "Content-Type": "application/json"
    }

    try:
        res = urequests.post(UBIDOTS_URL, json=data, headers=headers)
        res.close()
        print("Data terkirim ke Ubidots:", data)
    except Exception as e:
        print("Gagal kirim:", e)

# LOOP UTAMA
def loop():
    while True:
        try:
            dht_sensor.measure()
            temp = dht_sensor.temperature()
            hum = dht_sensor.humidity()
            light = deteksi_cahaya()

            print("Temp:", temp, "| Hum:", hum, "| Light:", light)

            led_suhu(temp)
            kirim_data(temp, hum, light)

            time.sleep(60)
        except Exception as e:
            print("Error:", e)

# MAIN PROGRAM 
def main():
    connect_wifi()
    loop()

main()	