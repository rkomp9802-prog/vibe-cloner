import streamlit as st
import yt_dlp
import os
import speech_recognition as sr
import requests

st.set_page_config(page_title="AI Video Reborn", page_icon="🎬")
st.title("🚀 AI Video Reborn: Полный Автомат")

# Сайдбар для настроек
with st.sidebar:
    st.header("⚙️ Настройки ИИ")
    api_key = st.text_input("ElevenLabs API Key", type="password")
    voice_id = st.text_input("Твой Voice ID")
    st.info("Куки активны. YouTube должен работать!")

video_url = st.text_input("🔗 Вставь ссылку на видео:")

if st.button("🔥 ЗАПУСТИТЬ ВСЁ САМО"):
    if not video_url or not api_key or not voice_id:
        st.error("❌ Заполни ссылку, API ключ и Voice ID!")
    else:
        status = st.empty()
        bar = st.progress(0)
        
        try:
            # --- ШАГ 1: АВТО-СКАЧИВАНИЕ ---
            status.write("⏳ Шаг 1: Скачиваю оригинал...")
            audio_wav = "source.wav"
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'temp_audio',
                'cookiefile': 'cookies.txt', # Твой паспорт для YouTube
                'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'wav'}],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            os.rename("temp_audio.wav", audio_wav)
            bar.progress(33)

            # --- ШАГ 2: АВТО-ТЕКСТ ---
            status.write("🎙️ Шаг 2: Слушаю и пишу текст...")
            r = sr.Recognizer()
            with sr.AudioFile(audio_wav) as source:
                audio_data = r.record(source)
                original_text = r.recognize_google(audio_data, language="ru-RU")
            st.info(f"Распознано: {original_text[:100]}...")
            bar.progress(66)

            # --- ШАГ 3: АВТО-ГОЛОС (ElevenLabs) ---
            status.write("🗣️ Шаг 3: Генерирую твой голос...")
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
            data = {
                "text": original_text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                with open("ai_voice.mp3", "wb") as f:
                    f.write(response.content)
                bar.progress(100)
                st.success("✅ Готово! Твой клон заговорил.")
                st.audio("ai_voice.mp3") # Можно сразу послушать результат
                st.download_button("📥 Скачать готовую озвучку", open("ai_voice.mp3", "rb"), "result.mp3")
            else:
                st.error(f"Ошибка ElevenLabs: {response.text}")

        except Exception as e:
            st.error(f"⚠️ Ошибка: {str(e)}")
