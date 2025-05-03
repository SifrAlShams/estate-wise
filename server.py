import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

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
        


@app.post("/transcribe/")
def transcribe_audio(request: FilePathRequest):
    try:
        print(request.file_path)
        transcript = transcribe_audio_file(request.file_path)
        print(transcript)
        
        return {
            'transcription': transcript
        }
    except FileNotFoundError:
        return {"error": f"File not found: {request.file_path}"}
    except Exception as e:
        return {"error": str(e)}


@app.post("/tts/")
def generate_tts(request: TextToSpeechRequest):
    try:
        print(f"TTS input text: {request.text}")
        audio_path = text_to_speech_file(request.text)
        print(f"Generated audio at: {audio_path}")

        return {
            "audio_path": audio_path
        }
    except Exception as e:
        return {"error": str(e)}
    
