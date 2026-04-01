import streamlit as st
import google.generativeai as genai
import requests
import os

# Настройка страницы
st.set_page_config(page_title="Конвейер v6.0", layout="wide")

# Пробуем загрузить ключи
try:
    GEMINI_KEY = st.secrets["GEMINI_KEY"].strip()
    ELEVEN_KEY = st.secrets["ELEVEN_KEY"].strip()
    VOICE_ID = st.secrets["VOICE_ID"].strip()
except Exception as e:
    st.error("Ошибка: Ключи не найдены в Secrets!")
    st.stop()

# Инициализация Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("🎬 Конвейер: Gemini + ElevenLabs")

uploaded_file = st.file_uploader("Загрузи видео", type=['mp4', 'mov'])

if st.button("🚀 ЗАПУСТИТЬ"):
    if uploaded_file:
        with st.status("Обработка...") as status:
            # 1. Заглушка для текста (так как STT требует ffmpeg в системе)
            # Если ты используешь готовый текст, вставь его сюда
            text_orig = "Что было бы если бы ты провел неделю в СССР..." 
            
            st.write(" Gemini пишет сценарий...")
            prompt = f"Сделай короткий виральный сценарий для Shorts из этого текста: {text_orig}"
            response = model.generate_content(prompt)
            final_text = response.text
            
            st.subheader("📝 Готовый сценарий:")
            st.write(final_text)
            
            st.write("🗣️ Озвучка ElevenLabs...")
            # Чистим текст от звездочек и лишних символов перед озвучкой
            clean_text = final_text.replace("*", "").replace("#", "")
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
            headers = {
                "xi-api-key": ELEVEN_KEY,
                "Content-Type": "application/json"
            }
            data = {
                "text": clean_text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
            }
            
            res = requests.post(url, json=data, headers=headers)
            
            if res.status_code == 200:
                st.audio(res.content, format='audio/mp3')
                st.success("Готово!")
            else:
                st.error(f"Ошибка ElevenLabs {res.status_code}: {res.text}")
    else:
        st.warning("Сначала загрузи файл!")
