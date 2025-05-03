import streamlit as st
from utils.take_sound_input import StreamlitMicRecorder
import uuid
import requests



BASE_URL = "http://localhost:8000/"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

file_name = str(uuid.uuid4())

st.title("🎙️ Streamlit Microphone Recorder")


if 'recorder' not in st.session_state:
    st.session_state.recorder = StreamlitMicRecorder(filename=f'{file_name}.wav')


for entry in st.session_state.chat_history:
    with st.chat_message("user"):
        st.audio(entry["user_audio"], format="audio/wav", start_time=0)
    with st.chat_message("assistant"):
        st.audio(entry["response_audio"], format="audio/wav", start_time=0)


st.markdown("-------------------------------------")
col1, col2 = st.columns([1, 5])
with col2:
    if st.button("🎤 Start Recording"):
        st.session_state.recorder.start()
        st.success("Recording started...")
    
    if st.button("Stop Recording"):
        st.session_state.recorder.stop()
        st.success(f"Recording stopped. Saved to {st.session_state.recorder.filename}")
        print("PATH TO INPUT AUDIO FILE: ", st.session_state.recorder.filename)

        input_file_path = st.session_state.recorder.filename

        with st.spinner("Transcribing and generating response..."):
            transcription_result = requests.post(f"{BASE_URL}/transcribe/", json={"file_path": input_file_path})
        
        if transcription_result.status_code == 200:
            input_transcript = transcription_result.text
            # agent call
            agent_api_result = requests.post(f"{BASE_URL}/get_agent_response/", json={"agent_input": input_transcript})
            if agent_api_result.status_code == 200:
                agent_data = agent_api_result.json()
                print(f"Agent Response: {agent_data['agent_response']}")
                print(f"Latency in agent: {agent_data['agent_latency']}")
                
                tts_api_result = requests.post(f"{BASE_URL}/tts/", json={"text": agent_data['agent_response']})
                tts_data = tts_api_result.json()
                output_audio_file = tts_data['audio_path']
                
                st.session_state.chat_history.append({
                    "user_audio": input_file_path,
                    "response_audio": output_audio_file
                })
                
                st.rerun()
        else:
            st.error("⚠️ Failed to process audio. Try again!")