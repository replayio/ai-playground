print("Importing modules...")
import pyaudio
import wave
import os
import numpy as np
import threading
import time
print("Modules imported successfully")

print("Initializing AudioRecording class...")
class AudioRecording:
    def __init__(self, file_name):
        print("Initializing AudioRecording...")
        print(f"Initializing AudioRecording with file_name: {file_name}")
        self.file_name = file_name
        self.is_recording = False
        self.frames = []
        self.audio = pyaudio.PyAudio()
        self.stream = None
        print("AudioRecording initialized")

    def start_recording(self):
        print("Starting recording...")
        print(f"[AudioRecording] Starting recording to file: {self.file_name}")
        self.is_recording = True
        self.frames = []
        print("Attempting to open PyAudio stream...")
        try:
            self.stream = self.audio.open(format=pyaudio.paInt16,
                                          channels=1,
                                          rate=44100,
                                          input=True,
                                          frames_per_buffer=1024)
            print("PyAudio stream opened successfully")
        except Exception as e:
            print(f"Error opening PyAudio stream: {str(e)}")
            return
        threading.Thread(target=self._record_thread).start()

    def stop_recording(self):
        print("Stopping recording...")
        print("[AudioRecording] Stopping recording")
        self.is_recording = False
        if self.stream:
            print("Stopping and closing PyAudio stream...")
            self.stream.stop_stream()
            self.stream.close()
            print("PyAudio stream stopped and closed")
        self._save_recording()

    def _save_recording(self):
        print(f"Saving recording to {self.file_name}...")
        print(f"[AudioRecording] Saving recording to file: {self.file_name}")
        try:
            wf = wave.open(self.file_name, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(self.frames))
            wf.close()
            print(f"Recording saved successfully to {self.file_name}")
        except Exception as e:
            print(f"Error saving recording: {str(e)}")

    def load_recording(self):
        print(f"Loading recording from {self.file_name}...")
        print(f"[AudioRecording] Loading recording from file: {self.file_name}")
        if not os.path.exists(self.file_name):
            print(f"[AudioRecording] File not found: {self.file_name}")
            return None
        try:
            with wave.open(self.file_name, 'rb') as wf:
                data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
            print(f"Recording loaded successfully from {self.file_name}")
            return data
        except Exception as e:
            print(f"Error loading recording: {str(e)}")
            return None

    def _record_thread(self):
        print("Record thread started...")
        print("Recording thread started")
        silence_threshold = 300
        silence_duration = 3  # seconds
        silence_count = 0
        while self.is_recording:
            try:
                data = self.stream.read(1024)
                self.frames.append(data)
                print(f"Recording... (frames: {len(self.frames)})")
                if self._is_silent(data, silence_threshold):
                    silence_count += 1
                else:
                    silence_count = 0
                if silence_count > silence_duration * 44100 / 1024:
                    print("Auto-stop: Silence detected")
                    self.stop_recording()
                    break
            except Exception as e:
                print(f"Error in recording thread: {str(e)}")
                self.stop_recording()
                break

    def _is_silent(self, data_chunk, threshold):
        print("Checking if audio is silent...")
        return np.max(np.abs(np.frombuffer(data_chunk, dtype=np.int16))) < threshold

    def get_audio_info(self):
        print("Getting audio info...")
        info = {
            'sample_width': self.audio.get_sample_size(pyaudio.paInt16),
            'channels': 1,
            'frame_rate': 44100,
            'num_frames': len(self.frames) if self.frames is not None else 0
        }
        print(f"Audio info: {info}")
        return info

if __name__ == "__main__":
    print("Creating AudioRecording instance...")
    audio_recorder = AudioRecording("test_recording.wav")
    print("Starting recording...")
    audio_recorder.start_recording()
    print("Sleeping for 5 seconds...")
    time.sleep(5)
    print("Stopping recording...")
    audio_recorder.stop_recording()
    print("Audio recording complete.")

# Example usage:
# recorder = AudioRecording("output.wav")
# recorder.start_recording()
# # Wait for some time or user input
# recorder.stop_recording()
# audio_data = recorder.load_recording()
# audio_info = recorder.get_audio_info()
