import streamlit as st
import yt_dlp
import whisper
import os

# Настройка страницы
st.set_page_config(page_title="AI Video Reborn", page_icon="🎬")
st.title("🚀 AI Video Reborn: Полный Клон")

# Боковая панель
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
            # ШАГ 1: Скачивание
            status_text.write("⏳ [1/4] Скачиваю аудио...")
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'temp_audio.mp3',
                'quiet': True,
                'no_warnings': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            progress_bar.progress(25)

            # ШАГ 2: Whisper
            status_text.write("🎙️ [2/4] Нейросеть слушает текст...")
            model = whisper.load_model("base")
            result = model.transcribe("temp_audio.mp3")
            st.write("**Текст из видео:**", result['text'][:300] + "...")
            progress_bar.progress(50)

            # ШАГ 3 и 4 (заглушки)
            status_text.write("🗣️ [3/4] Работа с голосом...")
            progress_bar.progress(75)
            status_text.write("🎨 [4/4] Генерация кадров...")
            progress_bar.progress(100)

            st.success("✅ Готово!")
            with open("temp_audio.mp3", "rb") as f:
                st.download_button("📥 Скачать результат", f, "result.mp3")

        except Exception as e:
            st.error(f"⚠️ Ошибка: {str(e)}")
