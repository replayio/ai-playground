import wave
import os
import numpy as np

class AudioRecording:
    def __init__(self, file_name):
        self.file_name = file_name
        self.frames = None
        self.sample_width = None
        self.channels = None
        self.frame_rate = None

    def load_recording(self):
        print(f"[AudioRecording] Loading recording from file: {self.file_name}")
        if not os.path.exists(self.file_name):
            raise FileNotFoundError(f"Recording file {self.file_name} not found.")

        with wave.open(self.file_name, 'rb') as wf:
            self.sample_width = wf.getsampwidth()
            self.channels = wf.getnchannels()
            self.frame_rate = wf.getframerate()
            self.frames = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        return self.frames

    def get_audio_info(self):
        return {
            'sample_width': self.sample_width,
            'channels': self.channels,
            'frame_rate': self.frame_rate,
            'num_frames': len(self.frames) if self.frames is not None else 0
        }

# Example usage:
# recorder = AudioRecording("input.wav")
# audio_data = recorder.load_recording()
# audio_info = recorder.get_audio_info()
