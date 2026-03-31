import streamlit as st
import yt_dlp
import whisper
import os
import time

# Настройка внешнего вида
st.set_page_config(page_title="AI Video Reborn", page_icon="🎬", layout="wide")

st.title("🚀 AI Video Reborn: Полный Клон")
st.subheader("Твой личный завод контента: голос, текст и видео")

# Боковая панель для ключей и настроек
with st.sidebar:
    st.header("⚙️ Настройки API")
    leo_key = st.text_input("Ключ Leonardo AI", type="password", help="Вставь сюда ключ за $5")
    eleven_key = st.text_input("Ключ ElevenLabs", type="password")
    voice_id = st.text_input("Voice ID (твой клон)", placeholder="Напр: pMsXv9S...")
    st.info("Эти ключи нужны для финальной сборки видео.")

# Основной интерфейс
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 1. Источник видео")
    video_url = st.text_input("🔗 Ссылка на YouTube:")
    st.write("--- или ---")
    uploaded_file = st.file_uploader("📥 Загрузи аудио вручную (если YouTube блокирует):", type=['mp3', 'wav', 'm4a'])

with col2:
    st.markdown("### 2. Управление")
    start_btn = st.button("🔥 ЗАПУСТИТЬ ПОЛНУЮ ПЕРЕДЕЛКУ", use_container_width=True)

# ПРОЦЕСС РАБОТЫ
if start_btn:
    if not video_url and not uploaded_file:
        st.error("❌ Ошибка: Вставь ссылку или загрузи файл!")
    else:
        status_text = st.empty()
        progress_bar = st.progress(0)
        
        try:
            # ЭТАП 1: ПОЛУЧЕНИЕ ФАЙЛА
            if uploaded_file:
                status_text.write("✅ Использую загруженный файл...")
                with open("temp_audio.mp3", "wb") as f:
                    f.write(uploaded_file.getbuffer())
            else:
                status_text.write("⏳ [1/4] Пытаюсь скачать аудио с YouTube...")
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': 'temp_audio.mp3',
                    'quiet': True,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
            
            progress_bar.progress(25)

            # ЭТАП 2: WHISPER (РАСПОЗНАВАНИЕ)
            status_text.write("🎙️
