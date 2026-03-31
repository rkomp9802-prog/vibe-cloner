import streamlit as st
import yt_dlp
import whisper
import os

# Настройка страницы
st.set_page_config(page_title="AI Video Reborn", page_icon="🎬")
st.title("🚀 AI Video Reborn: Полный Клон")

# Сайдбар
with st.sidebar:
    st.header("⚙️ Ключи API")
    leo_key = st.text_input("Ключ Leonardo", type="password")
    eleven_key = st.text_input("Ключ ElevenLabs", type="password")
    voice_id = st.text_input("Voice ID")

st.markdown("### Источник контента")
video_url = st.text_input("🔗 Ссылка на YouTube:")
uploaded_file = st.file_uploader("📥 Загрузи аудио вручную:", type=['mp3', 'wav', 'm4a'])

if st.button("🔥 НАЧАТЬ ТРАНСФОРМАЦИЮ"):
    if not video_url and not uploaded_file:
        st.error("❌ Нужно вставить ссылку или загрузить файл!")
    else:
        status = st.empty()
        bar = st.progress(0)
        
        try:
            # ШАГ 1
            if uploaded_file:
                status.write("✅ Файл получен.")
                with open("temp.mp3", "wb") as f:
                    f.write(uploaded_file.getbuffer())
            else:
                status.write("⏳ Скачиваю с YouTube...")
                ydl_opts = {'format': 'bestaudio/best', 'outtmpl': 'temp.mp3', 'quiet': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
            bar.progress(25)

            # ШАГ 2 (WHISPER)
            status.write("🎙️ ИИ расшифровывает текст...")
            model = whisper.load_model("tiny")
            result = model.transcribe("temp.mp3")
            
            bar.progress(60)
            st.success("✅ Текст готов!")
            st.info(result['text'])
            bar.progress(100)
            st.balloons()
            
        except Exception as e:
            st.error(f"⚠️ Ошибка: {str(e)}")
