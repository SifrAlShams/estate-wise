import pyaudio
import wave
import threading
import os



import os
os.environ['INPUT_SOUND_FILES_PATH'] = 'datafiles/recordings/'
input_files_dir = str(os.getenv('INPUT_SOUND_FILES_PATH'))
print(input_files_dir)



class StreamlitMicRecorder:
    def __init__(self, filename='output.wav', channels=1, rate=16000, frames_per_buffer=1024):
        self.filename = f'{input_files_dir}{filename}'
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self.frames = []
        self.recording = False
        self.thread = None

    def start(self):
        self.recording = True
        self.frames = []
        self.thread = threading.Thread(target=self._record)
        self.thread.start()

    def stop(self):
        self.recording = False
        self.thread.join()
        self._save()

    def _record(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.frames_per_buffer)

        while self.recording:
            data = stream.read(self.frames_per_buffer)
            self.frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def _save(self):
        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()
