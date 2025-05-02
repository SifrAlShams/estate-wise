import os
import json
from groq import Groq



client = Groq()

filename = os.path.dirname(__file__) + "/YOUR_AUDIO.wav"


with open(filename, "rb") as file:
    transcription = client.audio.transcriptions.create(
      file=file,
      model="whisper-large-v3-turbo",
      prompt="Specify context or spelling",  # Optional
      response_format="verbose_json",  # Optional
      timestamp_granularities = ["word", "segment"], # Optional (must set response_format to "json" to use and can specify "word", "segment" (default), or both)
      language="en",  # Optional
      temperature=0.0  # Optional
    )
    # To print only the transcription text, you'd use print(transcription.text) (here we're printing the entire transcription object to access timestamps)
    print(json.dumps(transcription, indent=2, default=str))

