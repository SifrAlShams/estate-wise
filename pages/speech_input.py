import streamlit as st
import requests
import uuid

BASE_URL = "http://localhost:8000/"

st.title("🎙️ Browser Mic Chat App")

audio_data = st.audio_input("🎤 Record a message")

if audio_data is not None:
    st.audio(audio_data, format="audio/wav")

    with st.spinner("Transcribing and generating response..."):
        response = requests.post(
            f"{BASE_URL}/transcribe/",
            files={"file": ("user_audio.wav", audio_data.getvalue(), "audio/wav")}
        )
        print("RESPONSE STATUS:", response.status_code)
        print("RESPONSE TEXT:", response.text)

        transcript = response.json()["transcription"]

        agent_result = requests.post(f"{BASE_URL}/get_agent_response/", json={"agent_input": transcript})
        agent_data = agent_result.json()

        tts_response = requests.post(f"{BASE_URL}/tts/", json={"text": agent_data["agent_response"]})
        if tts_response.status_code == 200:
            audio_bytes = tts_response.content  # The raw WAV bytes
            st.audio(audio_bytes, format="audio/wav")

