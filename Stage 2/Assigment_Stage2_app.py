from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId  # Untuk mengonversi ObjectId MongoDB ke string
import requests

app = Flask(__name__)

# Koneksi ke MongoDB Atlas
MONGO_USERNAME = "yogagautama"
MONGO_PASSWORD = "eskelapasaw1t"
MONGO_CLUSTER = "cluster-yoga.wfitb.mongodb.net"

MONGO_URI = f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_CLUSTER}/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)

db = client["Cluster-Yoga"]  
collection = db["Data_Sensor"]

# Konfigurasi Ubidots
UBIDOTS_TOKEN = "BBUS-SGtqPwDxvpv0n2nHCsZbyqRjP2kvVN" 
UBIDOTS_URL = "http://industrial.api.ubidots.com/api/v1.6/devices/esp32-cihuy-neuron"

@app.route("/data", methods=["POST"])
def receive_data():
    try:
        data = request.json  # Menerima data dari ESP32
        print("Received data:", data)

        # Simpan data ke MongoDB
        inserted = collection.insert_one(data)

        # Ubah ObjectId menjadi string agar bisa dikirim dalam JSON
        data["_id"] = str(inserted.inserted_id)

        # Kirim data ke Ubidots
        headers = {"Content-Type": "application/json", "X-Auth-Token": UBIDOTS_TOKEN}
        response = requests.post(UBIDOTS_URL, json=data, headers=headers)

        return jsonify({
            "status": "success",
            "ubidots_response": response.text,
            "mongo_id": data["_id"]
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2008,debug=True)