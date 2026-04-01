import streamlit as st
import google.generativeai as genai
import requests

# 1. Настройка страницы
st.set_page_config(page_title="Конвейер v7.0", layout="centered")
st.title("🎬 Конвейер: Gemini + ElevenLabs")

# 2. Безопасное получение ключей (с очисткой от пробелов)
try:
    GEMINI_KEY = st.secrets["GEMINI_KEY"].strip()
    ELEVEN_KEY = st.secrets["ELEVEN_KEY"].strip()
    VOICE_ID = st.secrets["VOICE_ID"].strip()
except Exception as e:
    st.error("Критическая ошибка: Ключи не найдены в Secrets!")
    st.stop()

# 3. Настройка Gemini (используем стабильный метод конфигурации)
try:
    genai.configure(api_key=GEMINI_KEY)
    # Используем модель flash, она самая быстрая и стабильная
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Ошибка настройки Gemini: {e}")

# Поле для ввода исходного текста (пока без STT, чтобы не падал интерфейс)
text_input = st.text_area("Введите идею для видео:", "Что было бы, если бы ты провел неделю в СССР в 1982 году?")

if st.button("🚀 ЗАПУСТИТЬ ГЕНЕРАЦИЮ"):
    with st.status("В процессе...") as status:
        
        # ШАГ 1: Gemini делает сценарий
        st.write("🤖 Gemini пишет виральный сценарий...")
        try:
            prompt = f"Напиши короткий динамичный сценарий для Shorts на основе этого текста: {text_input}. Используй эмодзи и короткие фразы."
            response = model.generate_content(prompt)
            final_text = response.text
            st.success("Сценарий готов!")
            st.markdown(f"**Текст сценария:**\n\n{final_text}")
        except Exception as e:
            st.error(f"Ошибка Gemini: {e}")
            st.stop()

        # ШАГ 2: ElevenLabs делает озвучку
        st.write("🗣️ ElevenLabs озвучивает...")
        
        # Показываем диагностику для контроля
        st.info(f"Диагностика ElevenLabs: отправляю ключ длиной {len(ELEVEN_KEY)} симв.")
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        headers = {
            "xi-api-key": ELEVEN_KEY,
            "Content-Type": "application/json"
        }
        # Убираем спецсимволы перед озвучкой
        clean_text = final_text.replace("*", "").replace("#", "")
        
        data = {
            "text": clean_text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
        }
        
        res = requests.post(url, json=data, headers=headers)
        
        if res.status_code == 200:
            st.audio(res.content, format='audio/mp3')
            st.success("Аудио успешно сгенерировано!")
        else:
            # Если опять 401 или другая ошибка — выводим детали
            st.error(f"Ошибка ElevenLabs ({res.status_code}): {res.text}")
