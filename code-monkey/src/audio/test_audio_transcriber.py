import os
import unittest
from audio_transcriber import AudioTranscriber
from audio_recording import AudioRecording  # Import the AudioRecording class


class TestAudioTranscriber(unittest.TestCase):
    def setUp(self):
        # Set the GOOGLE_APPLICATION_CREDENTIALS_JSON for the test environment
        os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"] = os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS_JSON"
        )

        # Initialize the AudioTranscriber
        self.transcriber = AudioTranscriber()

        # Corrected path to use absolute path
        self.test_audio_path = os.path.join(os.path.dirname(__file__), "test.wav")
        self.expected_transcription = "This is a test transcription."

    def test_transcription(self):
        recording = AudioRecording(
            self.test_audio_path
        )  # Create an AudioRecording object
        transcription = self.transcriber.get_transcript(
            recording
        )  # Pass the AudioRecording object
        self.assertEqual(transcription, self.expected_transcription)


if __name__ == "__main__":
    unittest.main()
