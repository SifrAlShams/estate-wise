import uuid

import streamlit as st
import requests
import pyaudio
import wave


# FastAPI Base URL
API_BASE_URL = "http://127.0.0.1:8000"

# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # Whisper prefers 16kHz
CHUNK = 1024
RECORD_SECONDS = 10
file_count = 0
OUTPUT_FILENAME = f"/home/user/PycharmProjects/real-estate-agent/data_files/voice_input_files/recorded_audio{file_count}.wav"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def record_audio():
    st.info("Recording...")
    global file_count
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        input_device_index=4,
                        frames_per_buffer=CHUNK)
    frames = []
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data_chunk = stream.read(CHUNK)
        frames.append(data_chunk)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    unique_id = uuid.uuid4().hex[:8]
    input_file_path = f"/home/user/PycharmProjects/real-estate-agent/data_files/voice_input_files/recorded_audio_{unique_id}.wav"

    with wave.open(input_file_path, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    return input_file_path


st.title("🎙️ Voice Chat Agent")
st.write("Record your voice message, and the agent will respond.")

for entry in st.session_state.chat_history:
        with st.chat_message("user"):
            st.audio(entry["user_audio"], format="audio/wav", start_time=0)
        with st.chat_message("assistant"):
            st.audio(entry["response_audio"], format="audio/wav", start_time=0)


st.markdown("-------------------------------------")
col1, col2 = st.columns([1, 5])
with col2:
    if st.button("🎤 Record & Send"):
        file_path = record_audio()
        with st.spinner("Transcribing and generating response..."):
            agent_response = requests.post(f"{API_BASE_URL}/get_agent_response/", json={"file_path": file_path})
        if agent_response.status_code == 200:
            data = agent_response.json()
            response_audio_path = data["voice_file_path"]
            st.session_state.chat_history.append({
                "user_audio": file_path,
                "response_audio": response_audio_path
            })
            st.rerun()
        else:
            st.error("⚠️ Failed to process audio. Try again!")