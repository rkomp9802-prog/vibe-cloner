import streamlit as st
import yt_dlp
import os
import speech_recognition as sr

st.set_page_config(page_title="AI Video Reborn", page_icon="🎬")
st.title("🚀 AI Video Reborn: Полный Клон")

with st.sidebar:
    st.header("⚙️ Настройки API")
    st.info("Автоматическое скачивание активировано через Cookies!")

st.markdown("### Источник контента")
video_url = st.text_input("🔗 Ссылка на YouTube:")

if st.button("🔥 НАЧАТЬ ТРАНСФОРМАЦИЮ"):
    if not video_url:
        st.error("❌ Вставьте ссылку!")
    else:
        status = st.empty()
        bar = st.progress(0)
        
        try:
            # ШАГ 1: Автоматическое скачивание с куками
            status.write("⏳ Обхожу защиту YouTube и скачиваю...")
            audio_path = "temp_audio.wav"
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'temp_download',
                'cookiefile': 'cookies.txt', # <-- НАШЕ СЕКРЕТНОЕ ОРУЖИЕ
                'quiet': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': '192',
                }],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            if os.path.exists("temp_download.wav"):
                os.rename("temp_download.wav", audio_path)
            
            bar.progress(50)

            # ШАГ 2: Распознавание текста
            if os.path.exists(audio_path):
                status.write("🎙️ ИИ расшифровывает текст...")
                r = sr.Recognizer()
                with sr.AudioFile(audio_path) as source:
                    audio_data = r.record(source)
                    text = r.recognize_google(audio_data, language="ru-RU")
                
                bar.progress(100)
                st.success("✅ Текст успешно получен!")
                st.info(text)
                st.balloons()
            else:
                st.error("❌ Ошибка: Файл не скачался.")
            
        except Exception as e:
            st.error(f"⚠️ Ошибка: {str(e)}")
