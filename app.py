import streamlit as st
import yt_dlp
import os
from speech_recognition import Recognizer, AudioFile

# Настройка страницы
st.set_page_config(page_title="AI Video Reborn", page_icon="🎬")
st.title("🚀 AI Video Reborn: Полный Клон")

with st.sidebar:
    st.header("⚙️ Ключи API")
    st.info("Ключи ElevenLabs понадобятся на следующем этапе")

st.markdown("### Источник контента")
video_url = st.text_input("🔗 Ссылка на YouTube:")
uploaded_file = st.file_uploader("📥 Или загрузи аудиофайл (WAV работает лучше всего):", type=['wav', 'mp3'])

if st.button("🔥 НАЧАТЬ ТРАНСФОРМАЦИЮ"):
    if not video_url and not uploaded_file:
        st.error("❌ Выберите источник!")
    else:
        status = st.empty()
        bar = st.progress(0)
        
        try:
            # ШАГ 1: Получение аудио
            status.write("⏳ Подготовка аудио...")
            audio_path = "temp_audio.wav"
            
            if uploaded_file:
                # Если загружен файл, сохраняем его
                with open("temp_input", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                # Конвертируем в нужный формат через системную команду
                os.system(f"ffmpeg -i temp_input -ar 16000 -ac 1 -y {audio_path}")
            else:
                # Скачиваем с YouTube сразу в WAV
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': 'temp_input',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'wav',
                        'preferredquality': '192',
                    }],
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                os.rename("temp_input.wav", audio_path)
            
            bar.progress(40)

            # ШАГ 2: Распознавание текста
            status.write("🎙️ ИИ расшифровывает текст...")
            r = Recognizer()
            with AudioFile(audio_path) as source:
                audio_data = r.record(source)
                text = r.recognize_google(audio_data, language="ru-RU")
            
            bar.progress(80)
            st.success("✅ Текст получен!")
            st.markdown("---")
            st.write("**Текст вашего видео:**")
            st.info(text)
            
            bar.progress(100)
            st.balloons()
            
        except Exception as e:
            st.error(f"⚠️ Ошибка: {str(e)}")
            st.info("Убедитесь, что вы создали файл packages.txt с текстом 'ffmpeg'.")
