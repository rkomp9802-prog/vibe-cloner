import streamlit as st
import os
import speech_recognition as sr
import requests
from pydub import AudioSegment
from openai import OpenAI

# --- ТВОИ ОБНОВЛЕННЫЕ КЛЮЧИ ---
DEFAULT_ELEVEN_KEY = "375561f84c040d79f3d7ccf5442529bcc35f88cc54e964da2f32a0fb3de493d3"
DEFAULT_VOICE_ID = "M1CSR3PJBsfWU6ZquG3C"
DEFAULT_GROK_KEY = "xai-TY5RCmyFtjPwTSk61SWGHXK0V4InmGRxmr8KCpDb1cDQCoFJL6kKScZlR83L9lXoiy1sVYXhlXhYGzFW"

st.set_page_config(page_title="Video AI Reborn v4.4", page_icon="🚀")
st.title("🎬 Конвейер Хайпа: Полный Автомат")

# Подтягиваем ключи
eleven_key = st.secrets.get("ELEVEN_KEY", DEFAULT_ELEVEN_KEY)
voice_id = st.secrets.get("VOICE_ID", DEFAULT_VOICE_ID)
grok_key = st.secrets.get("GROK_KEY", DEFAULT_GROK_KEY)

with st.sidebar:
    st.header("🔑 Доступ")
    st.success("✅ Все ключи настроены")
    st.info("Просто закинь видео и жди результат.")

uploaded_video = st.file_uploader("📥 Загрузи видео (MP4/MOV):", type=['mp4', 'mov', 'avi'])

if st.button("🔥 ПЕРЕРОДИТЬ КОНТЕНТ"):
    if not uploaded_video:
        st.error("❌ Загрузи файл!")
    else:
        status = st.empty()
        bar = st.progress(0)
        
        try:
            # 1. Звук
            status.write("⏳ Шаг 1: Извлекаю аудио...")
            with open("temp_video.mp4", "wb") as f:
                f.write(uploaded_video.getbuffer())
            os.system("ffmpeg -i temp_video.mp4 -ab 160k -ac 2 -ar 44100 -vn temp_audio.wav -y")
            bar.progress(25)

            # 2. Текст
            status.write("🎙️ Шаг 2: Распознаю речь...")
            r = sr.Recognizer()
            with sr.AudioFile("temp_audio.wav") as source:
                audio_data = r.record(source)
                raw_text = r.recognize_google(audio_data, language="ru-RU")
            st.write("**Оригинал:**", raw_text)
            bar.progress(50)

            # 3. Grok (Умный выбор модели)
            status.write("🤖 Шаг 3: Grok пишет сценарий...")
            client = OpenAI(api_key=grok_key, base_url="https://api.x.ai/v1")
            
            prompt = f"Перепиши этот текст для YouTube Shorts. Сделай его максимально захватывающим и виральным. Текст: {raw_text}"
            
            # Пробуем по очереди разные названия моделей, чтобы избежать ошибки 400
            success = False
            for model_name in ["grok-2-1212", "grok-2", "grok-beta"]:
                try:
                    completion = client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    final_text = completion.choices[0].message.content
                    st.success(f"✨ Сценарий готов (использована модель {model_name})")
                    success = True
                    break
                except Exception:
                    continue
            
            if not success:
                raise Exception("Ни одна модель Grok не ответила. Проверь баланс в xAI консоли.")
            
            st.write(final_text)
            bar.progress(75)

            # 4. Озвучка ElevenLabs
            status.write("🗣️ Шаг 4: Генерирую ИИ-голос...")
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
                st.download_button("📥 Скачать озвучку", open("result.mp3", "rb"), "result.mp3")
            else:
                st.error(f"Ошибка ElevenLabs: {res.text}")

        except Exception as e:
            st.error(f"⚠️ Ошибка: {str(e)}")
        
        # Чистим файлы
        for f in ["temp_video.mp4", "temp_audio.wav"]:
            if os.path.exists(f): os.remove(f)
