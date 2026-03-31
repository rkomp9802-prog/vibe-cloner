import streamlit as st
import yt_dlp
import os
import speech_recognition as sr
import requests
from pydub import AudioSegment

st.set_page_config(page_title="AI Video Reborn", page_icon="🎬")
st.title("🚀 AI Video Reborn: Полный Автомат")

# Боковая панель
with st.sidebar:
    st.header("⚙️ Настройки")
    api_key = st.text_input("ElevenLabs API Key", type="password")
    voice_id = st.text_input("Voice ID")
    st.warning("Убедись, что файл cookies.txt загружен на GitHub!")

video_url = st.text_input("🔗 Ссылка на YouTube (Shorts или Видео):")

if st.button("🔥 ЗАПУСТИТЬ ВСЁ САМО"):
    if not video_url or not api_key or not voice_id:
        st.error("❌ Заполни все поля в настройках!")
    else:
        status = st.empty()
        bar = st.progress(0)
        
        try:
            # --- ШАГ 1: СКАЧИВАНИЕ ---
            status.write("⏳ Шаг 1: Скачиваю звук с YouTube...")
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'audio_raw',
                'cookiefile': 'cookies.txt', # Твой файл с куками
                'noplaylist': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                }],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            audio_file = "audio_raw.wav"
            bar.progress(30)

            # --- ШАГ 2: РАСПОЗНАВАНИЕ (Легкий метод) ---
            status.write("🎙️ Шаг 2: Распознаю текст...")
            r = sr.Recognizer()
            with sr.AudioFile(audio_file) as source:
                audio_data = r.record(source)
                # Используем бесплатный движок Google для скорости
                text = r.recognize_google(audio_data, language="ru-RU")
            
            st.info(f"Текст распознан: {text[:200]}...")
            bar.progress(60)

            # --- ШАГ 3: ОЗВУЧКА ---
            status.write("🗣️ Шаг 3: Генерирую твой голос...")
            tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
            }
            
            response = requests.post(tts_url, json=data, headers=headers)
            
            if response.status_code == 200:
                with open("result.mp3", "wb") as f:
                    f.write(response.content)
                bar.progress(100)
                st.success("✅ Всё готово!")
                st.audio("result.mp3")
            else:
                st.error(f"Ошибка ElevenLabs: {response.text}")

        except Exception as e:
            st.error(f"⚠️ Произошла ошибка: {str(e)}")
        
        # Чистим временные файлы
        if os.path.exists("audio_raw.wav"):
            os.remove("audio_raw.wav")
