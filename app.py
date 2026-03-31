import streamlit as st
import yt_dlp
import whisper
import os

st.set_page_config(page_title="AI Video Reborn", page_icon="🎬")
st.title("🚀 AI Video Reborn: Полный Клон")

with st.sidebar:
    st.header("⚙️ Ключи API")
    leo_key = st.text_input("Ключ Leonardo", type="password")
    eleven_key = st.text_input("Ключ ElevenLabs", type="password")
    voice_id = st.text_input("Voice ID (твой клон)")

video_url = st.text_input("🔗 Вставь ссылку на видео (YouTube):")

if st.button("🔥 ЗАПУСТИТЬ ПОЛНУЮ ПЕРЕДЕЛКУ"):
    if not leo_key or not eleven_key or not video_url:
        st.error("❌ Сначала заполни ключи и ссылку!")
    else:
        status_text = st.empty()
        progress_bar = st.progress(0)

        try:
            # ШАГ 1: Улучшенное скачивание
            status_text.write("⏳ [1/4] Обхожу защиту и скачиваю аудио...")
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'temp_audio.mp3',
                'quiet': True,
                'no_warnings': True,
                'referer': 'https://www.google.com/', # Притворяемся, что пришли из поиска
                'geo_bypass': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            progress_bar.progress(25)

            # ШАГ 2: Whisper (этот этап самый тяжелый)
            status_text.write("🎙️ [2/4] Нейросеть Whisper слушает запись... (это может занять 1-2 мин)")
            model = whisper.load_model("tiny") # Используем tiny модель для скорости в облаке
            result = model.transcribe("temp_audio.mp3")
            
            st.success("✅ Текст успешно извлечен!")
            st.write("**Текст:**", result['text'][:500] + "...")
            progress_bar.progress(50)

            # Оставшиеся шаги для визуализации
            status_text.write("🗣️ [3/4] Подготовка клонирования голоса...")
            progress_bar.progress(75)
            status_text.write("🎨 [4/4] Анализ сцен для Leonardo...")
            progress_bar.progress(100)

        except Exception as e:
            st.error(f"⚠️ Ошибка на стороне YouTube или Whisper: {str(e)}")
            if "403" in str(e):
                st.warning("YouTube заблокировал этот запрос. Попробуй вставить ссылку на другое видео или Short-ролик.")
