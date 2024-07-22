import os
import unittest
from audio_transcriber import AudioTranscriber
from audio_recording import AudioRecording  # Import the AudioRecording class

class TestAudioTranscriber(unittest.TestCase):
    def setUp(self):
        # Set up the environment variable for Google Cloud credentials
        # using the credentials loaded by the AudioTranscriber class
        self.transcriber = AudioTranscriber()
        # Set the GOOGLE_APPLICATION_CREDENTIALS environment variable using the credentials JSON string from the environment
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')

        self.test_audio_path = 'test/test.wav'  # Corrected path
        self.expected_transcription = "This is a test transcription."

    def test_transcription(self):
        recording = AudioRecording(self.test_audio_path)  # Create an AudioRecording object
        transcription = self.transcriber.get_transcript(recording)  # Pass the AudioRecording object
        self.assertEqual(transcription, self.expected_transcription)

if __name__ == '__main__':
    unittest.main()
