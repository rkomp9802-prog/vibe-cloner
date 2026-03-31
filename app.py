import streamlit as st
import yt_dlp
import os
import speech_recognition as sr

# Настройка страницы
st.set_page_config(page_title="AI Video Reborn", page_icon="🎬")
st.title("🚀 AI Video Reborn: Полный Клон")

with st.sidebar:
    st.header("⚙️ Настройки API")
    st.info("Убедитесь, что файлы requirements.txt и packages.txt настроены верно.")

st.markdown("### Источник контента")
video_url = st.text_input("🔗 Ссылка на YouTube:")
uploaded_file = st.file_uploader("📥 Загрузи аудио (WAV или MP3):", type=['wav', 'mp3'])

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
                with open("temp_input", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                # Используем ffmpeg (из packages.txt) для конвертации
                os.system(f"ffmpeg -i temp_input -ar 16000 -ac 1 -y {audio_path}")
            else:
                status.write("⏳ Скачиваю с YouTube...")
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': 'temp_download',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'wav',
                        'preferredquality': '192',
                    }],
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                if os.path.exists("temp_download.wav"):
                    os.rename("temp_download.wav", audio_path)
            
            bar.progress(40)

            # ШАГ 2: Распознавание текста
            if os.path.exists(audio_path):
                status.write("🎙️ ИИ расшифровывает текст...")
                r = sr.Recognizer()
                with sr.AudioFile(audio_path) as source:
                    audio_data = r.record(source)
                    # Используем Google Speech Recognition (бесплатно)
                    text = r.recognize_google(audio_data, language="ru-RU")
                
                bar.progress(80)
                st.success("✅ Текст получен!")
                st.info(text)
                bar.progress(100)
                st.balloons()
            else:
                st.error("❌ Файл аудио не был создан. Проверьте packages.txt")
            
        except Exception as e:
            st.error(f"⚠️ Ошибка: {str(e)}")
