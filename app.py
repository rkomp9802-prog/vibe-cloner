import streamlit as st
import yt_dlp
import whisper
import os

# Настройка страницы
st.set_page_config(page_title="AI Video Reborn", page_icon="🎬")
st.title("🚀 AI Video Reborn: Полный Клон")

# Боковая панель
with st.sidebar:
    st.header("⚙️ Ключи API")
    leo_key = st.text_input("Ключ Leonardo", type="password")
    eleven_key = st.text_input("Ключ ElevenLabs", type="password")
    voice_id = st.text_input("Voice ID")

# Основная область
st.markdown("### 1. Выбери источник")
video_url = st.text_input("🔗 Ссылка на YouTube:")
uploaded_file = st.file_uploader("📥 Или загрузи свой аудиофайл (если YouTube блокирует):", type=['mp3', 'wav', 'm4a'])

if st.button("🔥 ЗАПУСТИТЬ ПЕРЕДЕЛКУ"):
    if not video_url and not uploaded_file:
        st.error("❌ Вставь ссылку или загрузи файл!")
    else:
        status = st.empty()
        bar = st.progress(0)
        
        try:
            # ШАГ 1: ПОЛУЧЕНИЕ АУДИО
            if uploaded_file:
                status.write("✅ Использую загруженный файл...")
                with open("temp.mp3", "wb") as f:
                    f.write(uploaded_file.getbuffer())
            else:
                status.write("⏳ Скачиваю с YouTube...")
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': 'temp.mp3',
                    'quiet': True,
                    'user_agent': 'Mozilla/5.0'
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
            
            bar.progress(25)

            # ШАГ 2: WHISPER (ТЕКСТ)
            status.write("🎙️ Нейросеть слушает... (это может занять время)")
            model = whisper.load_model("tiny")
            result = model.transcribe("temp.mp3")
            
            bar.progress(50)
            st.markdown("---")
            st.success("✅ Текст успешно распознан!")
            st.write(result['text'])
            st.markdown("---")

            # ШАГ 3 И 4 (ЗАГЛУШКИ)
            status.write("🗣️ Готовлю клонирование голоса...")
            bar.progress(75)
            status.write("🎨 Готовлю генерацию кадров...")
            bar.progress(100)
            
            st.balloons()
            
        except Exception as e:
            st.error(f"⚠️ Ошибка: {str(e)}")
            st.info("Если YouTube выдает 403, просто загрузи файл через кнопку выше.")
