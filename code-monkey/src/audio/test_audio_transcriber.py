import os
import unittest
from audio_transcriber import AudioTranscriber
from audio_recording import AudioRecording  # Import the AudioRecording class

class TestAudioTranscriber(unittest.TestCase):
    def setUp(self):
        self.transcriber = AudioTranscriber()
        self.test_audio_path = 'test/test.wav'  # Corrected path
        self.expected_transcription = "This is a test transcription."

    def test_transcription(self):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS_JSON'] = '{"type": "service_account", "project_id": "your-project-id", "private_key_id": "your-private-key-id", "private_key": "-----BEGIN PRIVATE KEY-----\\nYOUR_PRIVATE_KEY\\n-----END PRIVATE KEY-----\\n", "client_email": "your-client-email@your-project-id.iam.gserviceaccount.com", "client_id": "your-client-id", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs", "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-client-email%40your-project-id.iam.gserviceaccount.com"}'
        recording = AudioRecording(self.test_audio_path)  # Create an AudioRecording object
        transcription = self.transcriber.get_transcript(recording)  # Pass the AudioRecording object
        self.assertEqual(transcription, self.expected_transcription)

if __name__ == '__main__':
    unittest.main()
