import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from pydantic import BaseModel

import io

from agent import get_response
from utils.whisper_transcription import transcribe_audio_file
from utils.elevenlabs_tts import text_to_speech_file



app = FastAPI()

# Enable CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = {"configurable": {"thread_id": "1"}}

class GetResponse(BaseModel):
    agent_input: str

class FilePathRequest(BaseModel):
    file_path: str

class TextToSpeechRequest(BaseModel):
    text: str



@app.post("/get_agent_response/")
def get_agent_response(request: GetResponse):
    print(f"User Input: {request.agent_input}")
    
    agent_response, response_time = get_response(request.agent_input, config)
    
    return {
        'agent_response': agent_response,
        'agent_latency': response_time
    }
        

import tempfile
from fastapi import UploadFile, File
from fastapi.responses import JSONResponse


@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        # Save uploaded file to disk (Groq Whisper needs a path)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(await file.read())
            tmp.flush()
            temp_path = tmp.name

        # Transcribe using Groq (which expects file path)
        transcript = transcribe_audio_file(temp_path)
        return {"transcription": transcript}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})



@app.post("/tts/")
def generate_tts(request: TextToSpeechRequest):
    try:
        print(f"TTS input text: {request.text}")
        audio_path = text_to_speech_file(request.text)
        print(f"Generated audio at: {audio_path}")

        audio_bytes = open(audio_path, "rb").read()
        return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/wav")

    except Exception as e:
        return {"error": str(e)}
    
