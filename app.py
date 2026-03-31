import streamlit as st
import os

st.set_page_config(page_title="AI Video Reborn", page_icon="🎬")

st.title("🚀 AI Video Reborn: Полный Клон")
st.markdown("Вставь ссылку, и ИИ создаст **новое видео**: новый голос, новые кадры, уникальные субтитры.")

# Настройки в боковой панели
with st.sidebar:
    st.header("⚙️ Ключи API")
    leo_key = st.text_input("Leonardo AI Key", type="password")
    eleven_key = st.text_input("ElevenLabs Key", type="password")
    voice_id = st.text_input("Voice ID (твой клон голоса)")

# Поле для ссылки
video_url = st.text_input("🔗 Ссылка на видео (YouTube):")

if st.button("🔥 ЗАПУСТИТЬ ПОЛНУЮ ПЕРЕДЕЛКУ"):
    if not leo_key or not eleven_key or not video_url:
        st.error("Ошибка: Введи все ключи и ссылку!")
    else:
        st.info("🪄 Магия началась! Процесс пошел...")
        # Тут сайт вызывает функции клонирования, которые мы писали в Colab
        st.warning("Внимание: Полная генерация видео и голоса может занять 5-10 минут.")
