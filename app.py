import streamlit as st
import os
import speech_recognition as sr
import requests
from pydub import AudioSegment
from openai import OpenAI

# --- ТВОИ ЛИЧНЫЕ КЛЮЧИ (ВШИТЫ НАМЕРТВО) ---
DEFAULT_ELEVEN_KEY = "375561f84c040d79f3d7ccf5442529bcc35f88cc54e964da2f32a0fb3de493d3"
DEFAULT_VOICE_ID = "M1CSR3PJBsfWU6ZquG3C"
DEFAULT_GROK_KEY = "xai-9pbWPosRUy2Oo570pmyE1HrEPTjDfnQPKs8DCruGNSZhAKXzeiPM94MXUtp4X8tPMDA0SkGwgF93zApf"

st.set_page_config(page_title="AI Video Auto-Pilot v4.2", page_icon="🎬")
st.title("🎬 Конвейер Хайпа: Полный Автомат")

# Проверка наличия ключей (из кода или из Secrets)
eleven_key = st.secrets.get("ELEVEN_KEY", DEFAULT_ELEVEN_KEY)
voice_id = st.secrets.get("VOICE_ID", DEFAULT_VOICE_ID)
grok_key = st.secrets.get("GROK_KEY", DEFAULT_GROK_KEY)

# --- БОКОВАЯ ПАНЕЛЬ ---
with st.sidebar:
    st.header("🔑 Статус доступа")
    if all([eleven_key, voice_id, grok_key]):
        st.success("✅ Ключи активны")
    else:
        st.error("❌ Ошибка в ключах")
    st.info("Просто загрузи видео, остальное сделает ИИ.")

# --- ИНТЕРФЕЙС ЗАГРУЗКИ ---
uploaded_video = st.file_uploader("📥 Загрузи видео (MP4/MOV):", type=['mp4', 'mov', 'avi'])

if st.button("🔥 ЗАПУСТИТЬ ТРАНСФОРМАЦИЮ"):
    if not uploaded_video:
        st.error("❌ Выбери файл видео!")
    else:
        status = st.empty()
        bar = st.progress(0)
        
        try:
            # 1. Извлечение звука (нужен ffmpeg в packages.txt)
            status.write("⏳ Шаг 1: Извлекаю оригинальную дорожку...")
            with open("temp_video.mp4", "wb") as f:
                f.write(uploaded_video.getbuffer())
            os.system("ffmpeg -i temp_video.mp4 -ab 160k -ac 2 -ar 44100 -vn temp_audio.wav -y")
            bar.progress(25)

            # 2. Распознавание
            status.write("🎙️ Шаг 2: Распознаю речь...")
            r = sr.Recognizer()
            with sr.AudioFile("temp_audio.wav") as source:
                audio_data = r.record(source)
                raw_text = r.recognize_google(audio_data, language="ru-RU")
            st.write("**Оригинал:**", raw_text)
            bar.progress(50)

            # 3. Работа с Grok (Авто-подбор модели)
            status.write("🤖 Шаг 3: Grok переписывает сценарий...")
            client = OpenAI(api_key=grok_key, base_url="https://api.x.ai/v1")
            
            # Динамический поиск доступной модели
            try:
                available_models = client.models.list()
                # Ищем любую модель grok (grok-2, grok-beta и т.д.)
                active_model = next((m.id for m in available_models.data if "grok" in m.id), "grok-2")
            except Exception:
                active_model = "grok-2" # Запасной вариант

            prompt = f"Сделай этот текст максимально захватывающим для Shorts, используй стиль исторического или survival-хоррора. Текст: {raw_text}"
            
            completion = client.chat.completions.create(
                model=active_model,
                messages=[{"role": "user", "content": prompt}]
            )
            final_text = completion.choices[0].message.content
            st.success(f"✨ Сценарий готов (использована модель {active_model}):")
            st.write(final_text)
            bar.progress(75)

            # 4. Озвучка ElevenLabs
            status.write("🗣️ Шаг 4: Генерирую новый голос...")
            tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {"xi-api-key": eleven_key, "Content-Type": "application/json"}
            data = {
                "text": final_text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
            }
            
            res = requests.post(tts_url, json=data, headers=headers)
            if res.status_code == 200:
                with open("result.mp3", "wb") as f:
                    f.write(res.content)
                bar.progress(100)
                st.audio("result.mp3")
                st.download_button("📥 Скачать результат", open("result.mp3", "rb"), "voiceover.mp3")
            else:
                st.error(f"Ошибка ElevenLabs: {res.text}")

        except Exception as e:
            st.error(f"⚠️ Ошибка в процессе: {str(e)}")
        
        # Удаление временных файлов
        for f in ["temp_video.mp4", "temp_audio.wav"]:
            if os.path.exists(f): os.remove(f)
