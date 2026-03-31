import streamlit as st
import yt_dlp
import whisper
import os

# Базовые настройки страницы
st.set_page_config(page_title="AI Video Reborn", page_icon="🎬")
st.title("🚀 AI Video Reborn: Полный Клон")

# Сайдбар для будущих настроек
with st.sidebar:
    st.header("⚙️ Ключи API")
    leo_key = st.text_input("Ключ Leonardo", type="password")
    eleven_key = st.text_input("Ключ ElevenLabs", type="password")
    voice_id = st.text_input("Voice ID")

st.markdown("### Источник контента")
video_url = st.text_input("🔗 Ссылка на YouTube (если не сработает 403, загрузи файл ниже):")
uploaded_file = st.file_uploader("📥 Загрузи аудио вручную для теста:", type=['mp3', 'wav', 'm4a'])

if st.button("🔥 НАЧАТЬ ТРАНСФОРМАЦИЮ"):
    if not video_url and not uploaded_file:
        st.error("❌ Нужно либо вставить ссылку, либо загрузить файл!")
    else:
        status = st.empty()
        bar = st.progress(0)
        
        try:
            # ЭТАП 1: ПОЛУЧЕНИЕ ЗВУКА
            if uploaded_file:
                status.write("✅ Файл получен напрямую.")
                with open("temp.mp3", "wb") as f:
                    f.write(uploaded_file.getbuffer())
            else:
                status.write("⏳ Пытаюсь достучаться до YouTube...")
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': 'temp.mp3',
                    'quiet': True,
                    'no_warnings': True
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
            
            bar.progress(25)

            # ЭТАП 2: РАСПОЗНАВАНИЕ ТЕКСТА (WHISPER)
            status.write("🎙️ ИИ начал расшифровку... Пожалуйста, подожди.")
            model = whisper.load_model("tiny")
            result = model.transcribe("temp.mp3")
            
            bar.progress(60)
            st.success("✅ Текст готов!")
            st.write("**Текст из видео:**")
            st.info(result['text'])
            
            # ЭТАП 3 И 4 (ПОКА В РАЗРАБОТКЕ)
            status.write("⚙️ Подготовка следующих этапов...")
            bar.progress(100)
            st.balloons()
            
        except Exception as e:
            st.error(f"⚠️ Ошибка: {str(e)}")
            st.info("Если видишь '403 Forbidden', просто загрузи аудиофайл через кнопку выше.")
