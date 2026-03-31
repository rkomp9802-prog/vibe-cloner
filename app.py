import streamlit as st
import yt_dlp
import whisper
import os

st.set_page_config(page_title="AI Video Reborn", page_icon="🎬")
st.title("🚀 AI Video Reborn: Полный Клон")

# Настройки в боковой панели
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
        # Создаем элементы интерфейса
        status_text = st.empty()
        progress_bar = st.progress(0)

        # ШАГ 1: Скачивание аудио
        status_text.write("⏳ [1/4] Скачиваю аудио из видео...")
        ydl_opts = {'format': 'bestaudio/best', 'outtmpl': 'temp_audio.mp3', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        progress_bar.progress(25)

        # ШАГ 2: Текст через Whisper
        status_text.write("🎙️ [2/4] Нейросеть слушает и записывает текст...")
        model = whisper.load_model("base")
        result = model.transcribe("temp_audio.mp3")
        final_text = result['text']
        st.write("**Распознанный текст:**", final_text[:200] + "...") # Показываем кусочек
        progress_bar.progress(50)

        # ШАГ 3: Озвучка (Здесь будет запрос к ElevenLabs)
        status_text.write("🗣️ [3/4] Генерирую твой голос через ElevenLabs...")
        # (Временно имитируем, пока не пропишем твой Voice ID)
        progress_bar.progress(75)

        # ШАГ 4: Генерация видео (Здесь будет Leonardo)
        status_text.write("🎨 [4/4] Рисую уникальные кадры...")
        progress_bar.progress(100)

        st.success("✅ Клон готов! (Версия 1.0)")
        
        # Кнопка скачивания (пока для примера скачиваем аудио)
        with open("temp_audio.mp3", "rb") as file:
            st.download_button(label="📥 СКАЧАТЬ РЕЗУЛЬТАТ", data=file, file_name="ai_video_reborn.mp3")
