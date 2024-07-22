import pyaudio
import wave
import os
import numpy as np
import threading
import time
import random

class AudioRecording:
    def __init__(self, file_name, is_test_environment=False):
        self.file_name = file_name
        self.is_recording = False
        self.is_test_environment = is_test_environment
        self.audio = pyaudio.PyAudio() if not is_test_environment else None
        self.stream = None
        print(f"Initializing AudioRecording {'in test environment' if is_test_environment else 'with real audio'}")

    def start_recording(self):
        self.is_recording = True
        if self.is_test_environment:
            self.stream = self.SimulatedStream()
            print("Starting simulated recording")
        else:
            self.stream = self.audio.open(format=pyaudio.paInt16,
                                          channels=1,
                                          rate=44100,
                                          input=True,
                                          frames_per_buffer=1024)
            print("Starting real audio recording")
        self.file = wave.open(self.file_name, 'wb')
        self.file.setnchannels(1)
        self.file.setsampwidth(2)  # 16-bit audio
        self.file.setframerate(44100)
        threading.Thread(target=self._record_thread).start()

    def stop_recording(self):
        self.is_recording = False
        if self.stream:
            if not self.is_test_environment:
                self.stream.stop_stream()
            self.stream.close()
        if hasattr(self, 'file'):
            self.file.close()
        print("Recording stopped")

    def load_recording(self):
        if not os.path.exists(self.file_name):
            return None
        with wave.open(self.file_name, 'rb') as wf:
            data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        return data

    def _record_thread(self):
        silence_threshold = 300
        silence_duration = 3  # seconds
        silence_count = 0
        print(f"{'Simulated' if self.is_test_environment else 'Real'} recording thread started")
        while self.is_recording:
            data = self.stream.read(1024)
            self.file.writeframes(data)
            if self.is_test_environment:
                print(f"Writing simulated data chunk of size {len(data)} to file")
            if self._is_silent(data, silence_threshold):
                silence_count += 1
            else:
                silence_count = 0
            if silence_count > silence_duration * 44100 / 1024:
                print("Silence detected, stopping recording")
                self.stop_recording()
                break

    def _is_silent(self, data_chunk, threshold):
        return np.max(np.abs(np.frombuffer(data_chunk, dtype=np.int16))) < threshold

    def get_audio_info(self):
        with wave.open(self.file_name, 'rb') as wf:
            info = {
                'sample_width': wf.getsampwidth(),
                'channels': wf.getnchannels(),
                'frame_rate': wf.getframerate(),
                'num_frames': wf.getnframes()
            }
        return info

    class SimulatedStream:
        def read(self, chunk_size):
            return bytes([random.randint(0, 255) for _ in range(chunk_size)])

        def close(self):
            pass

if __name__ == "__main__":
    audio_recorder = AudioRecording("test_recording.wav", is_test_environment=True)
    audio_recorder.start_recording()
    time.sleep(5)
    audio_recorder.stop_recording()
