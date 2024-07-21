import wave
import os
import numpy as np
import threading
import time

class AudioRecording:
    def __init__(self, file_name='recording.wav'):
        self.file_name = file_name
        self.frames = []
        self.sample_width = 2
        self.channels = 1
        self.frame_rate = 44100
        self.is_recording = False
        self.simulate_recording = True
        print("[AudioRecording] Initializing in simulation mode.")

    def start_recording(self):
        print(f"[AudioRecording] Starting simulated recording to file: {self.file_name}")
        self.is_recording = True
        self.frames = []
        threading.Thread(target=self._simulate_record_thread).start()

    def stop_recording(self):
        print("[AudioRecording] Stopping recording")
        self.is_recording = False
        self._save_recording()



    def _simulate_record_thread(self):
        print("[AudioRecording] Simulating recording...")
        while self.is_recording:
            simulated_frame = np.random.randint(-32768, 32767, 1024).astype(np.int16).tobytes()
            self.frames.append(simulated_frame)
            time.sleep(0.023)  # Simulate ~44.1kHz sampling rate

    def _save_recording(self):
        print(f"[AudioRecording] Saving recording to file: {self.file_name}")
        wf = wave.open(self.file_name, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.sample_width)
        wf.setframerate(self.frame_rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        self.frames = np.frombuffer(b''.join(self.frames), dtype=np.int16)

    def load_recording(self):
        if self.frames is not None and len(self.frames) > 0:
            print(f"[AudioRecording] Using existing recording")
            return self.frames

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
            'num_frames': len(self.frames) if self.frames is not None else 0,
            'simulated': self.simulate_recording
        }

# Example usage:
# recorder = AudioRecording("output.wav")
# recorder.start_recording()
# # Wait for some time or user input
# recorder.stop_recording()
# audio_data = recorder.load_recording()
# audio_info = recorder.get_audio_info()
