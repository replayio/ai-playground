import speech_recognition as sr
from audio_recording import AudioRecording
import os
from google.oauth2 import service_account
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AudioTranscriber:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if credentials_path:
            self.credentials = service_account.Credentials.from_service_account_file(credentials_path)
        else:
            raise Exception("Cannot initialize AudioTranscriber. GOOGLE_APPLICATION_CREDENTIALS (env var) are missing.")
        logger.debug(f"Initialized AudioTranscriber with credentials: {self.credentials}")

    def get_transcript(self, recording: AudioRecording, language: str = "en-US") -> str:
        try:
            audio_data = recording.load_recording()
            audio_info = recording.get_audio_info()
            logger.debug(f"Audio info: {audio_info}")

            audio = sr.AudioData(audio_data.tobytes(), audio_info['frame_rate'], audio_info['sample_width'])
            logger.debug(f"Created AudioData object: {audio}")

            logger.info("[AudioTranscriber] Transcribing audio...")
            logger.debug(f"Credentials: {self.credentials}")
            logger.debug(f"Attempting to transcribe with language: {language}")

            credentials_json = self.credentials.to_json() if self.credentials else None
            logger.debug(f"Credentials JSON: {credentials_json}")

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
