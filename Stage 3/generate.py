from config import UBIDOTS_TOKEN, DEVICE_LABEL, BASE_URL, sensor_vars, count_vars, HEADERS
import requests
from datetime import datetime
import schedule
import time
import os

# Fungsi ambil data historis dengan timeout dan error handling lebih baik
def get_historical_data(variable, hours=24):
    """Mengambil data historis dari Ubidots dengan error handling yang lebih robust"""
    end = int(datetime.now().timestamp() * 1000)
    start = end - (hours * 60 * 60 * 1000)
    url = f"{BASE_URL}/{variable}/values?start={start}&end={end}&force=true"  
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=10) 
        res.raise_for_status()  
        return res.json().get("results", [])
    except requests.exceptions.RequestException as e:
        print(f"⚠ Gagal mengambil data {variable}: {str(e)}")
        return []
    except ValueError as e:
        print(f"⚠ Gagal parsing JSON untuk {variable}: {str(e)}")
        return []

# Fungsi generate pertanyaan dengan format yang konsisten
def generate_qa(var, values, is_count=False):
    """Generate QA pair dengan format yang konsisten"""

    variable_aliases = {
    "led_merah_count": "led red",
    "led_kuning_count": "led yellow",
    "led_hijau_count": "led green",
    "redup_count": "dim light",
    "temperature": "temperature",
    "humidity": "humidity",
    "light": "light"
    }
    # pastikan values diurutkan berdasarkan timestamp asc
    values = sorted(values, key=lambda d: d["timestamp"])
    num_values = [d["value"] for d in values if isinstance(d.get("value"), (int, float))]
    display_name = variable_aliases.get(var, var.replace("_", " "))
    qa_lines = []

    if is_count:
        # ambil saja nilai terakhir
        latest = int(num_values[-1]) if num_values else 0
        qa_lines.append(
            f"Q: How many times was {display_name} detected today? <|sep|> A: It was detected {int(latest)} times today.\n\n"
        )

    else:
        if num_values:
            avg = sum(num_values) / len(num_values)
            min_val = min(num_values)
            max_val = max(num_values)
            latest = num_values[-1]
            
            qa_lines.extend([
                f"Q: What is the average {display_name} today? <|sep|> A: The average is {avg:.2f}.\n\n",
                f"Q: What is the lowest {display_name} today? <|sep|> A: The lowest is {min_val}.\n\n",
                f"Q: What is the highest {display_name} today? <|sep|> A: The highest is {max_val}.\n\n",
                f"Q: What is the current {display_name}? <|sep|> A: The current value is {latest}.\n\n"
            ])
    
    return "".join(qa_lines)

def update_dataset():
    """Update dataset dengan logging yang lebih informatif"""
    try:
        # Buat folder data jika belum ada
        os.makedirs("data", exist_ok=True)
        
        with open("data/dataset_ubidots.txt", "w", encoding="utf-8") as f:
            # Sensor numerical
            for var in sensor_vars:
                data = get_historical_data(var)
                if data:
                    print(f"🔄 Memproses {var}: {len(data)} data points")
                f.write(generate_qa(var, data))
            
            # Counters
            for var in count_vars:
                data = get_historical_data(var)
                if data:
                    print(f"🔄 Memproses {var}: {len(data)} data points")
                f.write(generate_qa(var, data, is_count=True))
        
        print(f"✅ Dataset berhasil diupdate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Gagal update dataset: {str(e)}")

if __name__ == "__main__":
    print("🚀 Memulai Ubidots Dataset Updater")
    print(f"⏰ Akan update setiap 1 menit | Token: {UBIDOTS_TOKEN[:4]}...{UBIDOTS_TOKEN[-4:]}")

    update_dataset()

    schedule.every(1).minutes.do(update_dataset)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Program dihentikan oleh user")