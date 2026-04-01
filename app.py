import streamlit as st
import os
import speech_recognition as sr
import requests
from pydub import AudioSegment
from openai import OpenAI

# --- ТВОИ НАСТРОЙКИ (Способ 2) ---
# Если не хочешь возиться с Secrets, просто вставь ключи здесь:
DEFAULT_ELEVEN_KEY = "ВСТАВЬ_СЮДА_КЛЮЧ"
DEFAULT_VOICE_ID = "M1CSR3PJBsfWU6ZquG3C" # Твой ID из скриншота
DEFAULT_GROK_KEY = "ВСТАВЬ_СЮДА_КЛЮЧ_GROK"

st.set_page_config(page_title="AI Video Reborn v3.2", page_icon="🚀")
st.title("🎬 Конвейер Хайпа: Video + Grok + ElevenLabs")

# Пытаемся взять ключи из Secrets (Способ 1), если они там есть
sec_eleven = st.secrets.get("ELEVEN_KEY", DEFAULT_ELEVEN_KEY)
sec_voice = st.secrets.get("VOICE_ID", DEFAULT_VOICE_ID)
sec_grok = st.secrets.get("GROK_KEY", DEFAULT_GROK_KEY)

# --- БОКОВАЯ ПАНЕЛЬ ---
with st.sidebar:
    st.header("🔑 Ключи доступа")
    # Теперь поля заполняются автоматически
    eleven_key = st.text_input("ElevenLabs API Key", value=sec_eleven, type="password")
    voice_id = st.text_input("ElevenLabs Voice ID", value=sec_voice)
    grok_key = st.text_input("xAI (Grok) API Key", value=sec_grok, type="password")
    st.markdown("---")
    st.info("Ключи подставлены автоматически. Просто загрузи видео!")

# --- ИНТЕРФЕЙС ---
uploaded_video = st.file_uploader("📥 Загрузи видео (MP4/MOV):", type=['mp4', 'mov', 'avi'])

if st.button("🔥 ПЕРЕРОДИТЬ КОНТЕНТ"):
    if not all([eleven_key, voice_id, grok_key]) or "ВСТАВЬ" in str([eleven_key, grok_key]):
        st.error("❌ Ключи не настроены! Пропиши их в коде или введи вручную.")
    elif not uploaded_video:
        st.error("❌ Загрузи файл видео!")
    else:
        status = st.empty()
        bar = st.progress(0)
        
        try:
            # 1. Извлечение звука
            status.write("⏳ Шаг 1: Достаю звук из видео...")
            with open("temp_video.mp4", "wb") as f:
                f.write(uploaded_video.getbuffer())
            os.system("ffmpeg -i temp_video.mp4 -ab 160k -ac 2 -ar 44100 -vn temp_audio.wav -y")
            bar.progress(25)

            # 2. Распознавание текста
            status.write("🎙️ Шаг 2: Слушаю оригинал...")
            r = sr.Recognizer()
            with sr.AudioFile("temp_audio.wav") as source:
                audio_data = r.record(source)
                raw_text = r.recognize_google(audio_data, language="ru-RU")
            st.write("**Оригинальный текст:**", raw_text)
            bar.progress(50)

            # 3. Улучшение через Grok (Модель grok-2)
            status.write("🤖 Шаг 3: Grok делает текст хайповым...")
            client = OpenAI(api_key=grok_key, base_url="https://api.x.ai/v1")
            
            prompt = f"Перепиши этот текст для YouTube Shorts. Сделай его максимально захватывающим. Текст: {raw_text}"
            
            completion = client.chat.completions.create(
                model="grok-2", 
                messages=[{"role": "user", "content": prompt}]
            )
            final_text = completion.choices[0].message.content
            st.success("✨ Grok переписал сценарий:")
            st.write(final_text)
            bar.progress(75)

            # 4. Озвучка
            status.write("🗣️ Шаг 4: Генерирую новый голос...")
            tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {"xi-api-key": eleven_key, "Content-Type": "application/json"}
            data = {
                "text": final_text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.45, "similarity_boost": 0.8}
            }
            
            res = requests.post(tts_url, json=data, headers=headers)
            if res.status_code == 200:
                with open("result.mp3", "wb") as f:
                    f.write(res.content)
                bar.progress(100)
                st.audio("result.mp3")
                st.download_button("📥 Скачать озвучку", open("result.mp3", "rb"), "final.mp3")
            else:
                st.error(f"Ошибка ElevenLabs: {res.text}")

        except Exception as e:
            st.error(f"⚠️ Ошибка: {str(e)}")
        
        # Очистка
        for f in ["temp_video.mp4", "temp_audio.wav"]:
            if os.path.exists(f): os.remove(f)
