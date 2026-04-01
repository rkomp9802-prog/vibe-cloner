import streamlit as st
import os
import speech_recognition as sr
import requests
import google.generativeai as genai

# ПРОВЕРКА КЛЮЧЕЙ В СИСТЕМЕ
try:
    eleven_key = st.secrets["ELEVEN_KEY"]
    voice_id = st.secrets["VOICE_ID"]
    gemini_key = st.secrets["GEMINI_KEY"]
except Exception:
    st.error("❌ Ключи не найдены! Зайди в Settings -> Secrets на сайте Streamlit.")
    st.stop()

st.set_page_config(page_title="Конвейер v5.5", page_icon="🎬")
st.title("🎬 Конвейер: Gemini + ElevenLabs")

# Настройка Gemini с защитой от ошибок
genai.configure(api_key=gemini_key)
model = genai.GenerativeModel('gemini-1.5-flash')

uploaded_video = st.file_uploader("📥 Загрузи видео:", type=['mp4', 'mov'])

if st.button("🚀 ЗАПУСТИТЬ"):
    if not uploaded_video:
        st.error("❌ Выбери файл!")
    else:
        status = st.empty()
        try:
            # 1. Извлечение аудио
            status.write("⏳ Шаг 1: Извлекаю звук...")
            with open("temp_video.mp4", "wb") as f:
                f.write(uploaded_video.getbuffer())
            os.system("ffmpeg -i temp_video.mp4 -ab 160k -ac 2 -ar 44100 -vn temp_audio.wav -y")

            # 2. Распознавание
            status.write("🎙️ Шаг 2: Распознаю текст...")
            r = sr.Recognizer()
            with sr.AudioFile("temp_audio.wav") as source:
                audio_data = r.record(source)
                raw_text = r.recognize_google(audio_data, language="ru-RU")
            st.write("**Оригинал:**", raw_text)

            # 3. Работа Gemini
            status.write("♊ Шаг 3: Gemini делает текст хайповым...")
            response = model.generate_content(f"Сделай этот текст для Shorts виральным и коротким: {raw_text}")
            final_text = response.text
            st.success("✨ Сценарий готов!")
            st.write(final_text)

            # 4. Озвучка ElevenLabs
            status.write("🗣️ Шаг 4: Озвучка...")
            tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {"xi-api-key": eleven_key, "Content-Type": "application/json"}
            data = {"text": final_text, "model_id": "eleven_multilingual_v2"}
            res = requests.post(tts_url, json=data, headers=headers)
            
            if res.status_code == 200:
                with open("result.mp3", "wb") as f:
                    f.write(res.content)
                st.audio("result.mp3")
            else:
                st.error(f"Ошибка ElevenLabs: {res.status_code}")

        except Exception as e:
            st.error(f"⚠️ Ошибка: {str(e)}")
