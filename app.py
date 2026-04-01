import streamlit as st
import os
import speech_recognition as sr
import requests
import google.generativeai as genai

# --- ЗАГРУЗКА КЛЮЧЕЙ ИЗ SECRETS ---
try:
    eleven_key = st.secrets["ELEVEN_KEY"]
    voice_id = st.secrets["VOICE_ID"]
    gemini_key = st.secrets["GEMINI_KEY"]
except Exception:
    st.error("❌ Ключи не найдены в Secrets! Настрой их в панели Streamlit.")
    st.stop()

st.set_page_config(page_title="Конвейер v5.6", page_icon="🎬")
st.title("🎬 Конвейер: Gemini + ElevenLabs")

# Настройка Google AI
genai.configure(api_key=gemini_key)

# УМНЫЙ ПОДБОР МОДЕЛИ (Решает ошибку 404)
@st.cache_resource
def get_working_model():
    try:
        # Получаем список всех моделей, которые поддерживают генерацию контента
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Ищем 1.5 Flash, если нет - берем первую рабочую
        target = next((m for m in models if "gemini-1.5-flash" in m), models[0])
        return genai.GenerativeModel(target), target
    except Exception as e:
        st.error(f"Ошибка при поиске моделей: {e}")
        return None, None

model, model_name = get_working_model()

uploaded_video = st.file_uploader("📥 Загрузи видео:", type=['mp4', 'mov'])

if st.button("🚀 ЗАПУСТИТЬ"):
    if not uploaded_video or model is None:
        st.error("❌ Ошибка: Видео не загружено или ИИ недоступен.")
    else:
        status = st.empty()
        try:
            # 1. Звук
            status.write("⏳ Шаг 1: Извлекаю аудио...")
            with open("temp_video.mp4", "wb") as f:
                f.write(uploaded_video.getbuffer())
            os.system("ffmpeg -i temp_video.mp4 -ab 160k -ac 2 -ar 44100 -vn temp_audio.wav -y")

            # 2. Текст
            status.write("🎙️ Шаг 2: Распознаю речь...")
            r = sr.Recognizer()
            with sr.AudioFile("temp_audio.wav") as source:
                audio_data = r.record(source)
                raw_text = r.recognize_google(audio_data, language="ru-RU")
            st.write("**Оригинал:**", raw_text)

            # 3. Gemini (с новой логикой выбора модели)
            status.write(f"♊ Шаг 3: Работает {model_name}...")
            response = model.generate_content(f"Перепиши для Shorts: {raw_text}")
            final_text = response.text
            st.success("✨ Сценарий готов!")
            st.write(final_text)

            # 4. ElevenLabs
            status.write("🗣️ Шаг 4: Озвучка...")
            tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            res = requests.post(tts_url, json={"text": final_text, "model_id": "eleven_multilingual_v2"}, 
                                headers={"xi-api-key": eleven_key})
            
            if res.status_code == 200:
                with open("result.mp3", "wb") as f: f.write(res.content)
                st.audio("result.mp3")
            else:
                st.error(f"Ошибка озвучки: {res.status_code}")

        except Exception as e:
            st.error(f"⚠️ Ошибка: {str(e)}")
