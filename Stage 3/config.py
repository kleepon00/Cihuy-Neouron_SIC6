UBIDOTS_TOKEN = "BBUS-3QZt39CQQv31S8IiKsGcc2Uv8pJehX"
DEVICE_LABEL = "esp32_cihuy_neuron"

BASE_URL = f"https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}"
HEADERS = {
    "X-Auth-Token": UBIDOTS_TOKEN,
    "Content-Type": "application/json"
}

sensor_vars = ["temperature", "humidity", "light"]
count_vars = ["redup_count", "led_merah_count", "led_kuning_count", "led_hijau_count"]