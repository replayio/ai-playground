import logging
import speech_recognition as sr
from google.oauth2 import service_account
import os
import json
from audio_recording import AudioRecording

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AudioTranscriber:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        credentials_file_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_FILE_PATH')
        credentials_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')

        if credentials_file_path:
            self.credentials = service_account.Credentials.from_service_account_file(credentials_file_path)
        elif credentials_json:
            try:
                credentials_info = json.loads(credentials_json)
                self.credentials = service_account.Credentials.from_service_account_info(credentials_info)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON provided in GOOGLE_APPLICATION_CREDENTIALS_JSON")
        else:
            logger.warning("No Google Cloud credentials provided. Set either GOOGLE_APPLICATION_CREDENTIALS_FILE_PATH or GOOGLE_APPLICATION_CREDENTIALS_JSON")
            self.credentials = None
        logger.debug(f"Initialized AudioTranscriber with credentials: {self.credentials}")

    def get_transcript(self, recording: AudioRecording, language: str = "en-US") -> str:
        try:
            audio_data = recording.load_recording()
            audio_info = recording.get_audio_info()
            logger.debug(f"Audio info: {audio_info}")

            if audio_info.get('simulated', False):
                logger.info("[AudioTranscriber] Simulating transcription...")
                import time
                time.sleep(2)
                simulated_transcript = "This is a simulated transcription. The audio playground is working as expected."
                logger.info(f"Simulated transcript: {simulated_transcript}")
                return simulated_transcript

            audio = sr.AudioData(audio_data.tobytes(), audio_info['frame_rate'], audio_info['sample_width'])
            logger.debug(f"Created AudioData object: {audio}")

            if self.credentials is None:
                logger.warning("No Google Cloud credentials available. Unable to perform transcription.")
                return "Transcription unavailable due to missing credentials"

            logger.info("[AudioTranscriber] Transcribing audio...")
            logger.debug(f"Credentials: {self.credentials}")
            logger.debug(f"Attempting to transcribe with language: {language}")

            if isinstance(self.credentials, service_account.Credentials):
                credentials_json = self.credentials.to_json()
            else:
                credentials_json = json.dumps(self.credentials)
            logger.debug("Prepared credentials JSON for recognize_google_cloud")

            try:
                response = self.recognizer.recognize_google_cloud(
                    audio,
                    credentials_json=credentials_json,
                    language=language,
                    show_all=True
                )
                logger.debug(f"Raw response from recognize_google_cloud: {response}")
            except Exception as e:
                logger.exception("Exception occurred during recognize_google_cloud call")
                raise

            if not isinstance(response, dict):
                logger.warning("Response is not a dictionary")
                return "Could not transcribe the audio"

            transcript = response.get('results', [{}])[0].get('alternatives', [{}])[0].get('transcript', '')
            logger.debug(f"Extracted transcript: {transcript}")

            if not transcript:
                logger.warning("No transcript available in the response")
                return "No transcription available"

            logger.info(f"Final transcript: {transcript}")
            return transcript
        except sr.UnknownValueError:
            logger.error("Speech Recognition could not understand the audio")
            return "Speech Recognition could not understand the audio"
        except sr.RequestError as e:
            logger.error(f"Could not request results from Speech Recognition service: {e}")
            return f"Could not request results from Speech Recognition service; {e}"
        except Exception as e:
            logger.exception(f"Unexpected error during transcription: {e}")
            return f"An unexpected error occurred during transcription: {repr(e)}"
