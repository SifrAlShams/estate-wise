from dotenv import load_dotenv
load_dotenv()

import os
import uuid

from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs



ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
output_dir = os.getenv("OUTPUT_SOUND_FILES_PATH")
print(type(output_dir))


if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY environment variable not set")

client = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)


def text_to_speech_file(text: str) -> str:
    response = client.text_to_speech.convert(
        voice_id="pNInz6obpgDQGcFmaJgB",  # Adam pre-made voice
        optimize_streaming_latency="0",
        output_format="mp3_44100_128",
        text=text,
        model_id="eleven_turbo_v2",  # use the turbo model for low latency, for other languages use the `eleven_multilingual_v2`
        voice_settings=VoiceSettings(
            stability=0.5,
            similarity_boost=0.8,
            style=0.5,
            use_speaker_boost=True,
        ),
    )

    unique_id = uuid.uuid4().hex[:8]
    save_file_path = f"{output_dir}{unique_id}.wav"

    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    return save_file_path