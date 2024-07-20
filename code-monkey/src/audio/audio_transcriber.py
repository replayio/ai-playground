import speech_recognition as sr
import numpy as np
from audio_recording import AudioRecording

class AudioTranscriber:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def get_transcript(self, recording: AudioRecording) -> str:
        audio_data = recording.load_recording()
        audio = sr.AudioData(audio_data.tobytes(), 44100, 2)

        print("[AudioTranscriber] Transcribing audio...")
        try:
            transcript = self.recognizer.recognize_google(audio)
            return transcript
        except sr.UnknownValueError:
            return "Speech Recognition could not understand the audio"
        except sr.RequestError as e:
            return f"Could not request results from Speech Recognition service; {e}"
