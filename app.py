import streamlit as st
import os
import speech_recognition as sr
import requests
import google.generativeai as genai

# Подключение ключей из системы Secrets
try:
    eleven_key = st.secrets["ELEVEN_KEY"]
    voice_id = st.secrets["VOICE_ID"]
    gemini_key = st.secrets["GEMINI_KEY"]
except Exception:
    st.error("❌ Ключи не найдены в Secrets! Настрой их в панели управления Streamlit.")
    st.stop()

st.set_page_config(page_title="Hype-Machine v5.2", page_icon="♊")
st.title("🎬 Конвейер: Gemini + ElevenLabs")

# Настройка Gemini
genai.configure(api_key=gemini_key)
model = genai.GenerativeModel('gemini-1.5-flash')

uploaded_video = st.file_uploader("📥 Загрузи видео:", type=['mp4', 'mov'])

if st.button("🚀 ЗАПУСТИТЬ"):
    if not uploaded_video:
        st.error("❌ Сначала выбери файл!")
    else:
        status = st.empty()
        try:
            # 1. Извлечение аудио
            status.write("⏳ Шаг 1: Работа с аудио...")
            with open("temp_video.mp4", "wb") as f:
                f.write(uploaded_video.getbuffer())
            os.system("ffmpeg -i temp_video.mp4 -ab 160k -ac 2 -ar 44100 -vn temp_audio.wav -y")

            # 2. Распознавание речи
            status.write("🎙️ Шаг 2: Распознаю текст оригинала...")
            r = sr.Recognizer()
            with sr.AudioFile("temp_audio.wav") as source:
                audio_data = r.record(source)
                raw_text = r.recognize_google(audio_data, language="ru-RU")
            st.write("**Оригинал:**", raw_text)

            # 3. Gemini переписывает сценарий
            status.write("♊ Шаг 3: Gemini делает текст хайповым...")
            prompt = f"Перепиши этот текст для YouTube Shorts. Сделай его коротким и захватывающим. Текст: {raw_text}"
            response = model.generate_content(prompt)
            final_text = response.text
            st.success("✨ Сценарий готов!")
            st.write(final_text)

            # 4. Озвучка в ElevenLabs
            status.write("🗣️ Шаг 4: Генерирую ИИ-голос...")
            tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {"xi-api-key": eleven_key, "Content-Type": "application/json"}
            data = {
                "text": final_text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
            }
            res = requests.post(tts_url, json=data, headers=headers)
            if res.status_code == 200:
                with open("result.mp3", "wb") as f:
                    f.write(res.content)
                st.audio("result.mp3")
            else:
                st.error(f"Ошибка ElevenLabs: {res.text}")

        except Exception as e:
            st.error(f"⚠️ Ошибка: {str(e)}")
