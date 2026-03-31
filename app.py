import streamlit as st
import os
import speech_recognition as sr
import requests
from pydub import AudioSegment

st.set_page_config(page_title="AI Video Reborn", page_icon="🎬")
st.title("🎬 Video-to-Voice: Полный Автомат")

# Настройки в боковой панели
with st.sidebar:
    st.header("⚙️ Настройки ИИ")
    api_key = st.text_input("ElevenLabs API Key", type="password")
    voice_id = st.text_input("Voice ID")
    st.info("Просто загрузи видео, и я сделаю всё остальное.")

# Основной интерфейс
uploaded_video = st.file_uploader("📥 Загрузи свое видео (MP4, MOV, AVI):", type=['mp4', 'mov', 'avi'])

if st.button("🔥 ПЕРЕОЗВУЧИТЬ"):
    if not api_key or not voice_id:
        st.error("❌ Сначала введи API Key и Voice ID в боковом меню!")
    elif not uploaded_video:
        st.error("❌ Загрузи видеофайл!")
    else:
        status = st.empty()
        bar = st.progress(0)
        
        try:
            # Шаг 1: Сохранение видео и извлечение звука
            status.write("⏳ Извлекаю звук из видео...")
            with open("temp_video.mp4", "wb") as f:
                f.write(uploaded_video.getbuffer())
            
            # Используем ffmpeg для вытягивания чистого звука
            os.system("ffmpeg -i temp_video.mp4 -ab 160k -ac 2 -ar 44100 -vn temp_audio.wav -y")
            bar.progress(30)

            # Шаг 2: Распознавание текста
            status.write("🎙️ Распознаю текст...")
            r = sr.Recognizer()
            with sr.AudioFile("temp_audio.wav") as source:
                audio_data = r.record(source)
                text = r.recognize_google(audio_data, language="ru-RU")
            
            st.success("✅ Текст распознан!")
            st.text_area("Распознанный текст:", text, height=150)
            bar.progress(60)

            # Шаг 3: Генерация новой озвучки
            status.write("🗣️ Генерирую твой голос в ElevenLabs...")
            tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
            }
            
            response = requests.post(tts_url, json=data, headers=headers)
            
            if response.status_code == 200:
                with open("final_voice.mp3", "wb") as f:
                    f.write(response.content)
                bar.progress(100)
                st.success("🎉 Готово! Твой новый голос:")
                st.audio("final_voice.mp3")
                st.download_button("📥 Скачать озвучку", open("final_voice.mp3", "rb"), "result.mp3")
            else:
                st.error(f"Ошибка ElevenLabs: {response.text}")

        except Exception as e:
            st.error(f"⚠️ Ошибка: {str(e)}")
        
        # Уборка мусора
        for f in ["temp_video.mp4", "temp_audio.wav"]:
            if os.path.exists(f): os.remove(f)
