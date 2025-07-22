import sys
import os
import json
from groq import Groq

def transcribe_audio_file(filepath: str, prompt: str = "Specify context or spelling") -> dict:
    """
    Transcribes the given audio file using Groq's Whisper model.

    Args:
        filepath (str): Absolute path to the .wav audio file.
        prompt (str): Optional context or spelling for transcription.

    Returns:
        dict: A dictionary containing the transcription and timestamps.
    """

    client = Groq()

    with open(filepath, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=file,
            model="whisper-large-v3-turbo",
            prompt=prompt,
            response_format="verbose_json",
            timestamp_granularities=["word", "segment"],
            language="en",
            temperature=0.0
        )
    print(transcription.text)
    return transcription.text



# if __name__ == "__main__":
#     filepath = "/home/ubuntu/Documents/LLM/estate-wise/datafiles/recordings/0.wav"
#     result = transcribe_audio_file(filepath)
#     print(result)
#     print(type(result))