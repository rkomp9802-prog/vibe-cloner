import streamlit as st
import yt_dlp
import os
from speech_recognition import Recognizer, AudioFile
from pydub import AudioSegment

# Настройка страницы
st.set_page_config(page_title="AI Video Reborn", page_icon="🎬")
st.title("🚀 AI Video Reborn: Полный Клон")

# Сайдбар
with st.sidebar:
    st.header("⚙️ Ключи API")
    st.info("Ключи понадобятся на этапе сборки видео")

st.markdown("### Источник контента")
video_url = st.text_input("🔗 Ссылка на YouTube:")
uploaded_file = st.file_uploader("📥 Или загрузи аудиофайл:", type=['mp3', 'wav'])

if st.button("🔥 НАЧАТЬ ТРАНСФОРМАЦИЮ"):
    if not video_url and not uploaded_file:
        st.error("❌ Выберите источник!")
    else:
        status = st.empty()
        bar = st.progress(0)
        
        try:
            # ШАГ 1: Получение аудио
            status.write("⏳ Подготовка аудио...")
            if uploaded_file:
                with open("temp.mp3", "wb") as f:
                    f.write(uploaded_file.getbuffer())
            else:
                ydl_opts = {'format': 'bestaudio/best', 'outtmpl': 'temp.mp3', 'quiet': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
            
            # Конвертация в WAV для распознавания
            status.write("🔄 Обработка звука...")
            audio = AudioSegment.from_file("temp.mp3")
            audio.export("temp.wav", format="wav")
            bar.progress(40)

            # ШАГ 2: Распознавание текста (Легкий способ)
            status.write("🎙️ ИИ расшифровывает текст...")
            r = Recognizer()
            with AudioFile("temp.wav") as source:
                audio_data = r.record(source)
                text = r.recognize_google(audio_data, language="ru-RU")
            
            bar.progress(80)
            st.success("✅ Текст успешно получен!")
            st.markdown("---")
            st.write("**Текст вашего видео:**")
            st.info(text)
            st.markdown("---")
            
            bar.progress(100)
            st.balloons()
            
        except Exception as e:
            st.error(f"⚠️ Ошибка: {str(e)}")
            st.info("Попробуйте загрузить короткий файл (до 1 минуты) для теста.")
