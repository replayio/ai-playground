import pyaudio
import wave
import os
import numpy as np
import threading

class AudioRecording:
    def __init__(self, file_name):
        self.file_name = file_name
        self.is_recording = False
        self.frames = []
        self.audio = pyaudio.PyAudio()
        self.stream = None

    def start_recording(self):
        self.is_recording = True
        self.frames = []
        print(f"[AudioRecording] Starting recording to file: {self.file_name}")
        self.stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        threading.Thread(target=self._record_thread).start()

    def stop_recording(self):
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self._save_recording()
        print(f"[AudioRecording] Stopped recording. Saved to file: {self.file_name}")

    def load_recording(self):
        print(f"[AudioRecording] Loading recording from file: {self.file_name}")
        with wave.open(self.file_name, 'rb') as wf:
            return np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)

    def _record_thread(self):
        silence_threshold = 300
        silence_duration = 3  # seconds
        silence_count = 0

        while self.is_recording:
            data = self.stream.read(1024)
            self.frames.append(data)

            if self._is_silent(data, silence_threshold):
                silence_count += 1
            else:
                silence_count = 0

            if silence_count > silence_duration * 44100 / 1024:
                print("Auto-stop: Silence detected")
                self.stop_recording()
                break

    def _is_silent(self, data_chunk, threshold):
        return np.max(np.abs(np.frombuffer(data_chunk, dtype=np.int16))) < threshold

    def _save_recording(self):
        with wave.open(self.file_name, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(self.frames))

# Example usage:
# recorder = AudioRecording("output.wav")
# recorder.start_recording()
# # Wait for some time or user input
# recorder.stop_recording()
# audio_data = recorder.load_recording()
