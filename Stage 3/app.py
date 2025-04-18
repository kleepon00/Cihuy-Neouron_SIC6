from config import UBIDOTS_TOKEN, DEVICE_LABEL, BASE_URL, sensor_vars, count_vars, HEADERS
import streamlit as st
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import re
import requests
import os 
from datetime import datetime
from difflib import get_close_matches

# Load model GPT-2 fine-tuned
@st.cache_resource
def load_custom_bot():
    model_dir = "model_train/gpt2-finetuned"
    if not os.path.exists(model_dir):
        st.error(f"Folder model tidak ditemukan: {model_dir}")
        st.stop()
    tokenizer = GPT2Tokenizer.from_pretrained(model_dir)
    model = GPT2LMHeadModel.from_pretrained(model_dir)
    return tokenizer, model

# Fungsi ambil data historis
def get_historical_data(variable, hours=24):
    end = int(datetime.now().timestamp() * 1000)
    start = end - (hours * 60 * 60 * 1000)
    url = f"{BASE_URL}/{variable}/values?start={start}&end={end}"
    try:
        res = requests.get(url, headers=HEADERS)
        return res.json().get("results", [])
    except:
        return []

@st.cache_data(ttl=60)
def get_data():
    data = {}
    # Ambil data terakhir dari setiap variabel
    for var in sensor_vars + count_vars:
        historical = get_historical_data(var, hours=24)
        if historical:
           latest = sorted(historical, key=lambda x: x['timestamp'], reverse=True)[0] 
           data[var] = latest["value"]
        else:
            data[var] = None
    return data

def generate_answer(prompt, tokenizer=None, model=None):
    with open("data/dataset_ubidots.txt", "r") as f:
        dataset = f.read()
    
    # Ekstrak semua pertanyaan dari dataset
    qa_pairs = [qa.strip() for qa in dataset.split("\n\n") if qa.strip()]
    questions = [qa.split("<|sep|>")[0].strip() for qa in qa_pairs]
    answers = [qa.split("<|sep|>")[-1].strip() for qa in qa_pairs]
    
    # Cari pertanyaan yang paling mirip (fuzzy matching)
    matches = get_close_matches(
        prompt.lower(), 
        [q.lower().replace("q: ", "") for q in questions],
        n=1, 
        cutoff=0.6
    )
    
    if matches:
        best_match_idx = [q.lower() for q in questions].index(f"q: {matches[0].lower()}")
        return answers[best_match_idx]
    else:
        return "I don't have information about that. Try asking with 'today' in your question."

def main():
    st.title("💡 Tanya Chatbot IoT dengan GPT-2")
    tokenizer, model = load_custom_bot()
    data = get_data()
    
    if data:
        st.subheader("📊 Data Sensor 24 Jam Terakhir")
        cols = st.columns(2)
        
        # Variabel yang ingin ditampilkan saja
        displayed_vars = ["temperature", "humidity", "light"]
        
        for i, var in enumerate(displayed_vars):
            val = data.get(var)
            if val is not None:
                cols[i % 2].metric(var.replace('_', ' ').title(), f"{val:.2f}")
            else:
                cols[i % 2].metric(var.replace('_', ' ').title(), "N/A")

    
    prompt_user = st.text_input("Tanyakan tentang data sensor (Gunakan Bahasa Inggris):")
    if st.button("Jawab") and prompt_user:
        response = generate_answer(prompt_user, tokenizer, model)
        st.success(response)

if __name__ == "__main__":
    main()