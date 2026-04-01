import streamlit as st
import os
import speech_recognition as sr
import requests
from pydub import AudioSegment
from openai import OpenAI

# --- ТВОИ ЛИЧНЫЕ КЛЮЧИ (ПРОПИШИ ОДИН РАЗ) ---
# Вставь свои ключи между кавычками:
DEFAULT_ELEVEN_KEY = "СЮДА_ВСТАВЬ_КЛЮЧ_ELEVENLABS"
DEFAULT_VOICE_ID = "M1CSR3PJBsfWU6ZquG3C" # Твой ID уже здесь
DEFAULT_GROK_KEY = "СЮДА_ВСТАВЬ_КЛЮЧ_GROK"

st.set_page_config(page_title="AI Video Auto-Pilot", page_icon="🎬")
st.title("🎬 Конвейер Хайпа: Полный Автомат")

# Проверка Secrets (если решишь использовать их позже)
sec_eleven = st.secrets.get("ELEVEN_KEY", DEFAULT_ELEVEN_KEY)
sec_voice = st.secrets.get("VOICE_ID", DEFAULT_VOICE_ID)
sec_grok = st.secrets.get("GROK_KEY", DEFAULT_GROK_KEY)

# --- БОКОВАЯ ПАНЕЛЬ ---
with st.sidebar:
    st.header("🔑 Ключи доступа")
    eleven_key = st.text_input("ElevenLabs API Key", value=sec_eleven, type="password")
    voice_id = st.text_input("ElevenLabs Voice ID", value=sec_voice)
    grok_key = st.text_input("xAI (Grok) API Key", value=sec_grok, type="password")
    st.info("Ключи сохранены. Просто загружай видео!")

# --- ИНТЕРФЕЙС ---
uploaded_video = st.file_uploader("📥 Загрузи видео (MP4/MOV):", type=['mp4', 'mov', 'avi'])

if st.button("🔥 ПЕРЕРОДИТЬ КОНТЕНТ"):
    if not all([eleven_key, voice_id, grok_key]) or "СЮДА_ВСТАВЬ" in str([eleven_key, grok_key]):
        st.error("❌ Сначала пропиши ключи в коде!")
    elif not uploaded_video:
        st.error("❌ Файл не выбран!")
    else:
        status = st.empty()
        bar = st.progress(0)
        
        try:
            # 1. Извлечение звука (требует ffmpeg в packages.txt)
            status.write("⏳ Шаг 1: Извлекаю оригинальный звук...")
            with open("temp_video.mp4", "wb") as f:
                f.write(uploaded_video.getbuffer())
            os.system("ffmpeg -i temp_video.mp4 -ab 160k -ac 2 -ar 44100 -vn temp_audio.wav -y")
            bar.progress(25)

            # 2. Распознавание
            status.write("🎙️ Шаг 2: Распознаю текст...")
            r = sr.Recognizer()
            with sr.AudioFile("temp_audio.wav") as source:
                audio_data = r.record(source)
                raw_text = r.recognize_google(audio_data, language="ru-RU")
            st.write("**Оригинал:**", raw_text)
            bar.progress(50)

            # 3. Улучшение через Grok (Исправленная модель)
            status.write("🤖 Шаг 3: Grok пишет сценарий...")
            client = OpenAI(api_key=grok_key, base_url="https://api.x.ai/v1")
            
            completion = client.chat.completions.create(
                model="grok-beta", # Изменено с grok-2 для исправления ошибки
                messages=[{"role": "user", "content": f"Сделай этот текст виральным для Shorts, сохранив смысл: {raw_text}"}]
            )
            final_text = completion.choices[0].message.content
            st.success("✨ Новый сценарий готов!")
            st.write(final_text)
            bar.progress(75)

            # 4. Озвучка в ElevenLabs
            status.write("🗣️ Шаг 4: Создаю ИИ-озвучку...")
            tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {"xi-api-key": eleven_key, "Content-Type": "application/json"}
            data = {
                "text": final_text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
            }
            
            res = requests.post(tts_url, json=data, headers=headers)
            if res.status_code == 200:
                with open("result.mp3", "wb") as f:
                    f.write(res.content)
                bar.progress(100)
                st.audio("result.mp3")
                st.download_button("📥 Скачать озвучку", open("result.mp3", "rb"), "final.mp3")
            else:
                st.error(f"Ошибка ElevenLabs: {res.text}")

        except Exception as e:
            st.error(f"⚠️ Ошибка: {str(e)}")
        
        # Удаление временных файлов
        for f in ["temp_video.mp4", "temp_audio.wav"]:
            if os.path.exists(f): os.remove(f)
