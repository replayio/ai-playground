import unittest
import tempfile
import json
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock
from audio_recording import AudioRecording
from audio_transcriber import AudioTranscriber


class TestAudioTranscriber(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_recording.wav")
        self.test_wav_path = os.path.join(os.path.dirname(__file__), "test.wav")

        # Set up mock Google Cloud credentials
        self.mock_credentials = MagicMock()

        # Clear any existing environment variables
        if "GOOGLE_APPLICATION_CREDENTIALS_JSON" in os.environ:
            del os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
        if "GOOGLE_APPLICATION_CREDENTIALS_PATH" in os.environ:
            del os.environ["GOOGLE_APPLICATION_CREDENTIALS_PATH"]

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        os.rmdir(self.temp_dir)
        # Clean up environment variables
        if "GOOGLE_APPLICATION_CREDENTIALS_JSON" in os.environ:
            del os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
        if "GOOGLE_APPLICATION_CREDENTIALS_PATH" in os.environ:
            del os.environ["GOOGLE_APPLICATION_CREDENTIALS_PATH"]

    def test_audio_recording(self):
        recording = AudioRecording(self.test_file, is_test_environment=True)
        recording.start_recording()
        recording.stop_recording()

        self.assertTrue(
            os.path.exists(self.test_file), "Recording file was not created"
        )
        self.assertGreater(
            os.path.getsize(self.test_file), 0, "Recording file is empty"
        )

    @patch("speech_recognition.Recognizer.recognize_google_cloud")
    @patch("audio_transcriber.service_account.Credentials.from_service_account_info")
    def test_transcribe_audio(
        self, mock_from_service_account_info, mock_recognize_google_cloud
    ):
        # Mock the recognize_google_cloud method
        mock_recognize_google_cloud.return_value = "This is a test transcription."

        # Mock the credentials
        mock_credentials = MagicMock()
        mock_from_service_account_info.return_value = mock_credentials

        # Create a mock audio file
        mock_audio_file = MagicMock()
        mock_audio_file.get_wav_data.return_value = b"mock audio data"
        mock_audio_file.get_audio_info.return_value = {
            "frame_rate": 44100,
            "sample_width": 2,
        }

        # Create a minimal mock credentials JSON
        mock_credentials_json = json.dumps(
            {
                "type": "service_account",
                "project_id": "test",
                "private_key_id": "test",
                "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC7/UoL8Iu1fTBN\n-----END PRIVATE KEY-----\n",
                "client_email": "test@test.iam.gserviceaccount.com",
                "client_id": "test",
            }
        )

        # Set up the environment variable
        os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"] = mock_credentials_json

        # Create an instance of AudioTranscriber
        transcriber = AudioTranscriber()

        # Call the get_transcript method
        result = transcriber.get_transcript(mock_audio_file)

        # Assert that the mock method was called with the correct arguments
        mock_recognize_google_cloud.assert_called_once_with(
            unittest.mock.ANY,  # AudioData object
            credentials=mock_credentials,
            language="en-US",
        )
        self.assertEqual(
            result,
            "This is a test transcription.",
            "Transcription result does not match expected output",
        )

        # Verify that the credentials were created from the mock JSON
        mock_from_service_account_info.assert_called_once()

        # Clean up environment variable
        del os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"]

    @patch("audio_transcriber.service_account.Credentials.from_service_account_info")
    def test_credential_handling(self, mock_from_service_account_info):
        mock_from_service_account_info.return_value = self.mock_credentials

        # Test with valid credentials
        valid_credentials_json = '{"type": "service_account", "project_id": "test", "private_key_id": "test", "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC7/UoL8Iu1fTBN\\nxnNKKtHJbNm8O4Czw5wHrZp3GsSJ5txsunnyABCDEFGHIJKLMNOPQRSTUVWXYZ01\\n23456789012345678901234567890123456789012345678901234567890123==\\n-----END PRIVATE KEY-----\\n", "client_email": "test@test.iam.gserviceaccount.com", "client_id": "test", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs", "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/test%40test.iam.gserviceaccount.com"}'
        os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"] = valid_credentials_json
        transcriber = AudioTranscriber()
        self.assertIsNotNone(
            transcriber.credentials, "Credentials should not be None with valid JSON"
        )
        mock_from_service_account_info.assert_called_once()

        # Test with invalid credentials
        os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"] = "invalid_json"
        transcriber = AudioTranscriber()
        self.assertIsNone(
            transcriber.credentials, "Credentials should be None with invalid JSON"
        )

        # Test with missing credentials
        if "GOOGLE_APPLICATION_CREDENTIALS_JSON" in os.environ:
            del os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
        transcriber = AudioTranscriber()
        self.assertIsNone(
            transcriber.credentials, "Credentials should be None with missing JSON"
        )


if __name__ == "__main__":
    unittest.main()


class TestAudioTranscriber(unittest.TestCase):
    # ... (previous methods)

    @patch("speech_recognition.Recognizer.recognize_google_cloud")
    def test_invalid_audio_data(self, mock_recognize_google_cloud):
        """
        Test that the AudioTranscriber correctly handles invalid audio data
        by raising a ValueError when attempting to transcribe it.
        """
        mock_credentials = MagicMock()
        print("DEBUG: Created mock credentials")

        with patch.object(
            AudioTranscriber, "_load_credentials", return_value=mock_credentials
        ):
            transcriber = AudioTranscriber()
            print(f"DEBUG: Created transcriber: {transcriber}")

            mock_recognize_google_cloud.side_effect = ValueError("Invalid audio data")
            print("DEBUG: Set side_effect for mock_recognize_google_cloud")

            invalid_audio = MagicMock()
            invalid_audio.load_recording.return_value = b"invalid audio data"
            invalid_audio.get_audio_info.return_value = {
                "frame_rate": 44100,
                "sample_width": 2,
            }

            print("DEBUG: About to call get_transcript")
            with self.assertRaises(ValueError):
                transcriber.get_transcript(invalid_audio)
            print("DEBUG: ValueError was raised as expected")

        print("DEBUG: Test completed")
        invalid_audio.load_recording.assert_called_once()
        invalid_audio.get_audio_info.assert_called_once()
        mock_recognize_google_cloud.assert_called_once()
