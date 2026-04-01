import streamlit as st
import google.generativeai as genai
import requests

# 1. Чтение конфигов с защитой от пробелов
GEMINI_KEY = st.secrets["GEMINI_KEY"].strip()
ELEVEN_KEY = st.secrets["ELEVEN_KEY"].strip()
VOICE_ID = st.secrets["VOICE_ID"].strip()

# 2. Настройка Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_audio(text):
    # Диагностика (та самая синяя плашка)
    st.info(f"Диагностика: ключ 'sk_{ELEVEN_KEY[3:7]}***', длина: {len(ELEVEN_KEY)} симв.")
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_KEY
    }
    
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        return response.content
    else:
        # Вывод подробной ошибки для отладки
        st.error(f"Ошибка {response.status_code}: {response.text}")
        return None
