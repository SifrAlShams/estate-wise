import os
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from agent import get_response



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

class FilePathRequest(BaseModel):
    file_path: str

@app.post("/get_agent_response/")
def get_agent_response(request: FilePathRequest):
    start_time = time.time()
    user_input = request.file_path

    print(f"User Input: {user_input}")
    agent_response, response_time = get_response(user_input, config)
    end_time = time.time()
    print(f"Latency: {end_time - start_time}")
    print(f"Agent Response: {agent_response}")

    return {"agent_response": agent_response}