import streamlit as st
import os
import speech_recognition as sr
import requests
import google.generativeai as genai

# --- ТВОИ КЛЮЧИ (БЕЗОПАСНО ИЗ SECRETS) ---
try:
    eleven_key = st.secrets["ELEVEN_KEY"]
    voice_id = st.secrets["VOICE_ID"]
    gemini_key = st.secrets["GEMINI_KEY"] # Заменили GROK_KEY на GEMINI_KEY
except Exception:
    st.error("⚠️ Настрой ключи (ELEVEN_KEY, VOICE_ID, GEMINI_KEY) в Secrets!")
    st.stop()

st.set_page_config(page_title="Gemini Video Editor v5.0", page_icon="♊")
st.title("🎬 Конвейер: Gemini + ElevenLabs")

# Настройка Gemini
genai.configure(api_key=gemini_key)
model = genai.GenerativeModel('gemini-1.5-flash')

uploaded_video = st.file_uploader("📥 Загрузи видео:", type=['mp4', 'mov'])

if st.button("🔥 ЗАПУСТИТЬ ЧЕРЕЗ GEMINI"):
    if not uploaded_video:
        st.error("❌ Выбери файл!")
    else:
        status = st.empty()
        bar = st.progress(0)
        
        try:
            # 1. Звук
            status.write("⏳ Шаг 1: Извлекаю аудио...")
            with open("temp_video.mp4", "wb") as f:
                f.write(uploaded_video.getbuffer())
            os.system("ffmpeg -i temp_video.mp4 -ab 160k -ac 2 -ar 44100 -vn temp_audio.wav -y")
            bar.progress(25)

            # 2. Текст
            status.write("🎙️ Шаг 2: Распознаю речь...")
            r = sr.Recognizer()
            with sr.AudioFile("temp_audio.wav") as source:
                audio_data = r.record(source)
                raw_text = r.recognize_google(audio_data, language="ru-RU")
            st.write("**Оригинал:**", raw_text)
            bar.progress(50)

            # 3. Gemini пишет сценарий
            status.write("♊ Шаг 3: Gemini делает магию...")
            prompt = f"Перепиши этот текст для YouTube Shorts. Сделай его максимально захватывающим и коротким. Стиль: survival-horror. Текст: {raw_text}"
            
            response = model.generate_content(prompt)
            final_text = response.text
            
            st.success("✨ Сценарий от Gemini готов:")
            st.write(final_text)
            bar.progress(75)

            # 4. Озвучка ElevenLabs
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
                bar.progress(100)
                st.audio("result.mp3")
                st.download_button("📥 Скачать озвучку", open("result.mp3", "rb"), "gemini_voice.mp3")
            else:
                st.error(f"Ошибка ElevenLabs: {res.text}")

        except Exception as e:
            st.error(f"⚠️ Ошибка: {str(e)}")
        
        for f in ["temp_video.mp4", "temp_audio.wav"]:
            if os.path.exists(f): os.remove(f)
