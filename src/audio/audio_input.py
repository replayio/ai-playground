from audio_recording import AudioRecording
from audio_transcriber import AudioTranscriber
import os

class AudioInput:
    default_file_name = "temp_audio.wav"

    def __init__(self):
        self.recording = None
        self.transcriber = AudioTranscriber()

    def get_input(self) -> str:
        print("[AudioInput] Initializing audio recording...")
        self.recording = AudioRecording(self.default_file_name)
        self.recording.start_recording()
        input("Press Enter to stop recording...")
        self.recording.stop_recording()

        print("[AudioInput] Audio recording completed. Transcribing...")
        transcript = self.transcriber.get_transcript(self.recording)
        print(f"[AudioInput] Transcription result: {transcript}")
        self._cleanup()
        return transcript

    def _cleanup(self):
        if self.recording and os.path.exists(self.default_file_name):
            os.remove(self.default_file_name)
            print(f"[AudioInput] Cleaned up temporary audio file: {self.default_file_name}")
        self.recording = None
