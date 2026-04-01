import streamlit as st
import os
import speech_recognition as sr
import requests
import google.generativeai as genai

# --- 1. ЗАГРУЗКА КЛЮЧЕЙ ИЗ SECRETS ---
try:
    eleven_key = st.secrets["ELEVEN_KEY"]
    voice_id = st.secrets["VOICE_ID"]
    gemini_key = st.secrets["GEMINI_KEY"]
except Exception as e:
    st.error(f"❌ Ошибка загрузки Secrets. Проверь настройки в Streamlit! Детали: {e}")
    st.stop()

# --- 2. НАСТРОЙКА ИНТЕРФЕЙСА ---
st.set_page_config(page_title="Конвейер v5.9", page_icon="🎬")
st.title("🎬 Конвейер: Gemini + ElevenLabs")

# --- 3. НАСТРОЙКА GEMINI ---
genai.configure(api_key=gemini_key)

try:
    # Ищем любую доступную модель, приоритет отдаем 1.5-flash
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    model_name = next((m for m in models if "gemini-1.5-flash" in m), models[0])
    model = genai.GenerativeModel(model_name)
except Exception as e:
    st.error(f"❌ Ошибка при подключении к Gemini: {e}")
    st.stop()

# --- 4. ОСНОВНАЯ ЛОГИКА ПРИЛОЖЕНИЯ ---
uploaded_video = st.file_uploader("📥 Загрузи видео (MP4/MOV):", type=['mp4', 'mov'])

if st.button("🚀 ЗАПУСТИТЬ"):
    if not uploaded_video:
        st.warning("⚠️ Пожалуйста, сначала загрузи видео!")
        st.stop()
    
    status = st.empty()
    try:
        # ШАГ 1: Извлечение аудио
        status.write("⏳ Шаг 1: Извлекаю аудио через FFmpeg...")
        with open("temp_video.mp4", "wb") as f:
            f.write(uploaded_video.getbuffer())
        os.system("ffmpeg -i temp_video.mp4 -ab 160k -ac 2 -ar 44100 -vn temp_audio.wav -y")
        
        # ШАГ 2: Распознавание текста
        status.write("🎙️ Шаг 2: Распознаю речь (Google STT)...")
        r = sr.Recognizer()
        with sr.AudioFile("temp_audio.wav") as source:
            audio_data = r.record(source)
            text_orig = r.recognize_google(audio_data, language="ru-RU")
        
        # ШАГ 3: Рерайт через Gemini
        status.write(f"♊ Шаг 3: Gemini ({model_name}) пишет сценарий...")
        prompt = f"Сделай этот текст коротким, виральным и динамичным для YouTube Shorts. Добавь эмодзи. Оригинал: {text_orig}"
        res_gemini = model.generate_content(prompt)
        final_text = res_gemini.text
        
        st.write("✨ **Готовый сценарий:**")
        st.write(final_text)

        # ШАГ 4: Озвучка через ElevenLabs
        status.write("🗣️ Шаг 4: ElevenLabs генерирует голос...")
        
        # Блок диагностики ключа ElevenLabs (выведет инфу на экран)
        key_preview = eleven_key[:4] + "***" if isinstance(eleven_key, str) and len(eleven_key) > 4 else "ПУСТО_ИЛИ_ОШИБКА"
        key_length = len(eleven_key) if isinstance(eleven_key, str) else 0
        st.info(f"⚙️ Диагностика ключа ElevenLabs: отправляю ключ '{key_preview}', длина: {key_length} симв.")

        # Настройки запроса
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": eleven_key,
            "Content-Type": "application/json"
        }
        payload = {
            "text": final_text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
        }
        
        # Отправка на сервер
        response = requests.post(url, json=payload, headers=headers)
        
        # Обработка ответа
        if response.status_code == 200:
            with open("out.mp3", "wb") as f:
                f.write(response.content)
            status.empty() # Убираем статус
            st.success("🎉 Озвучка успешно создана!")
            st.audio("out.mp3")
            st.balloons()
        elif response.status_code == 401:
            st.error("❌ Ошибка 401: ElevenLabs не принял твой ключ. Убедись, что скопировал его без пробелов и сохранил в Secrets!")
        else:
            st.error(f"❌ Ошибка ElevenLabs {response.status_code}: {response.text}")
            
    except Exception as e:
        st.error(f"⚠️ Произошла непредвиденная ошибка: {e}")
