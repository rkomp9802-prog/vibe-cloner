import streamlit as st
import os
import speech_recognition as sr
import requests
from pydub import AudioSegment
from openai import OpenAI

# Настройка страницы
st.set_page_config(page_title="Hype-Machine v4.5", page_icon="🚀")
st.title("🎬 Конвейер Хайпа: Полный Автомат")

# --- БЕЗОПАСНОЕ ПОДКЛЮЧЕНИЕ КЛЮЧЕЙ ---
# Теперь программа берет ключи из Settings -> Secrets в Streamlit
try:
    eleven_key = st.secrets["ELEVEN_KEY"]
    voice_id = st.secrets["VOICE_ID"]
    grok_key = st.secrets["GROK_KEY"]
except Exception:
    st.error("⚠️ Ключи не найдены в Secrets! Настрой их в панели управления Streamlit.")
    st.stop()

with st.sidebar:
    st.header("🔑 Статус доступа")
    st.success("✅ Ключи загружены из системы")
    st.info("Это самый безопасный способ работы.")

# --- ОСНОВНАЯ ЛОГИКА ---
uploaded_video = st.file_uploader("📥 Загрузи видео (MP4/MOV):", type=['mp4', 'mov', 'avi'])

if st.button("🔥 ПЕРЕРОДИТЬ КОНТЕНТ"):
    if not uploaded_video:
        st.error("❌ Сначала выбери файл!")
    else:
        status = st.empty()
        bar = st.progress(0)
        
        try:
            # 1. Извлечение звука (нужен ffmpeg в packages.txt)
            status.write("⏳ Шаг 1: Извлекаю аудио...")
            with open("temp_video.mp4", "wb") as f:
                f.write(uploaded_video.getbuffer())
            os.system("ffmpeg -i temp_video.mp4 -ab 160k -ac 2 -ar 44100 -vn temp_audio.wav -y")
            bar.progress(25)

            # 2. Распознавание речи
            status.write("🎙️ Шаг 2: Распознаю текст...")
            r = sr.Recognizer()
            with sr.AudioFile("temp_audio.wav") as source:
                audio_data = r.record(source)
                raw_text = r.recognize_google(audio_data, language="ru-RU")
            st.write("**Оригинал:**", raw_text)
            bar.progress(50)

            # 3. Работа с Grok (Авто-выбор модели)
            status.write("🤖 Шаг 3: Grok пишет сценарий...")
            client = OpenAI(api_key=grok_key, base_url="https://api.x.ai/v1")
            
            prompt = f"Перепиши этот текст для YouTube Shorts. Сделай его максимально захватывающим и виральным. Текст: {raw_text}"
            
            # Пробуем доступные модели по очереди
            success_grok = False
            for model_name in ["grok-2-1212", "grok-2", "grok-beta"]:
                try:
                    completion = client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    final_text = completion.choices[0].message.content
                    st.success(f"✨ Сценарий готов (модель {model_name})")
                    success_grok = True
                    break
                except:
                    continue
            
            if not success_grok:
                st.error("❌ Ошибка: Grok не смог подобрать модель. Проверь баланс xAI.")
                st.stop()
            
            st.write(final_text)
            bar.progress(75)

            # 4. Озвучка ElevenLabs
            status.write("🗣️ Шаг 4: Генерирую финальный голос...")
            tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {"xi-api-key": eleven_key, "Content-Type": "application/json"}
            data = {
                "text": final_text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
            }
            
            res = requests.post(tts_url, json=data, headers=headers)
            if res.status_code == 200:
                with open("result.mp3", "wb") as f:
                    f.write(res.content)
                bar.progress(100)
                st.audio("result.mp3")
                st.download_button("📥 Скачать результат", open("result.mp3", "rb"), "final_voice.mp3")
            else:
                st.error(f"Ошибка ElevenLabs: {res.text}")

        except Exception as e:
            st.error(f"⚠️ Произошла ошибка: {str(e)}")
        
        # Уборка
        for f in ["temp_video.mp4", "temp_audio.wav"]:
            if os.path.exists(f): os.remove(f)
