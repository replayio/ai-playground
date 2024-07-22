import logging
import os
import json
import time
import base64
import binascii
import textwrap
import tempfile
import speech_recognition as sr
from google.oauth2 import service_account
from google.auth.exceptions import DefaultCredentialsError
from pyasn1.error import PyAsn1Error
from audio_recording import AudioRecording

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AudioTranscriber:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.credentials = self._load_credentials()
        self.recognizer.credentials = self.credentials

    def _load_credentials(self):
        logger.debug("Attempting to load Google Cloud credentials")
        credentials_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')

        logger.debug(f"GOOGLE_APPLICATION_CREDENTIALS_JSON: {credentials_json}")

        if credentials_json:
            logger.debug("Found GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable")
            credentials = self._load_credentials_from_json(credentials_json)
            if credentials:
                logger.debug("Successfully loaded credentials from JSON")
            else:
                logger.debug("Failed to load credentials from JSON")
            return credentials
        else:
            logger.warning("No Google Cloud credentials provided. Set GOOGLE_APPLICATION_CREDENTIALS_JSON")
            return None

        logger.debug(f"Final credentials state: {'Loaded' if self.credentials else 'Not loaded'}")

    def _load_credentials_from_json(self, credentials_json):
        logger.debug(f"Received credentials JSON string of length: {len(credentials_json)}")
        try:
            logger.debug("Attempting to parse credentials JSON")
            credentials_info = json.loads(credentials_json)
            logger.debug(f"Parsed credentials keys: {', '.join(credentials_info.keys())}")

            required_keys = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email', 'client_id']
            for key in required_keys:
                if key not in credentials_info:
                    logger.error(f"Required key '{key}' not found in credentials JSON")
                    return None

            private_key = credentials_info.get('private_key', '')
            logger.debug(f"Private key length: {len(private_key)}")
            if not private_key:
                logger.error("Private key is empty")
                return None

            formatted_key = self._format_private_key(private_key)
            if not formatted_key:
                logger.error("Failed to format private key")
                return None

            logger.debug(f"Formatted key length: {len(formatted_key)}")
            credentials_info['private_key'] = formatted_key

            try:
                logger.debug("Attempting to create credentials from service account info")
                credentials = service_account.Credentials.from_service_account_info(credentials_info)
                logger.debug("Successfully created credentials object")
            except Exception as e:
                logger.error(f"Failed to create credentials object: {str(e)}")
                return None

            logger.debug(f"Returning credentials of type: {type(credentials)}")
            return credentials

        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {str(e)}")
        except KeyError as e:
            logger.error(f"Missing required field in credentials JSON: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error creating credentials: {e}")
        return None

    def _format_private_key(self, private_key):
        try:
            logger.debug(f"Original private key length: {len(private_key)}")

            # Check if the key is already properly formatted
            if private_key.startswith('-----BEGIN PRIVATE KEY-----') and private_key.endswith('-----END PRIVATE KEY-----\n'):
                logger.debug("Private key is already properly formatted")
                return private_key

            # Remove any existing newlines and spaces
            cleaned_key = ''.join(private_key.split())
            logger.debug(f"Cleaned key length: {len(cleaned_key)}")

            # Extract the key content between PEM headers
            start = cleaned_key.find('PRIVATEKEY-----') + 15
            end = cleaned_key.rfind('-----ENDPRIVATE')
            if start == 14 or end == -1:  # Check if headers are missing
                logger.error("Private key is missing proper PEM headers")
                return None
            key_content = cleaned_key[start:end]
            logger.debug(f"Extracted key content length: {len(key_content)}")

            # Ensure the key content is valid base64
            try:
                decoded = base64.b64decode(key_content, validate=True)
            except binascii.Error as e:
                logger.error(f"Invalid base64 in private key: {str(e)}")
                return None

            encoded = base64.b64encode(decoded).decode('utf-8')
            logger.debug(f"Re-encoded key length: {len(encoded)}")

            # Wrap the base64 content to 64 characters per line
            wrapped = '\n'.join(textwrap.wrap(encoded, 64))

            # Add PEM headers
            formatted_key = f"-----BEGIN PRIVATE KEY-----\n{wrapped}\n-----END PRIVATE KEY-----\n"

            logger.debug(f"Final formatted key length: {len(formatted_key)}")
            logger.debug(f"Formatted key first 10 chars: {formatted_key[:10]}...")
            logger.debug(f"Formatted key last 10 chars: ...{formatted_key[-11:]}")

            # Validate the formatted key
            if not self._validate_private_key(formatted_key):
                logger.error("Formatted key failed validation")
                return None

            return formatted_key
        except Exception as e:
            logger.exception(f"Unexpected error formatting private key: {str(e)}")
            return None

    def _validate_private_key(self, private_key):
        try:
            from cryptography.hazmat.primitives.serialization import load_pem_private_key
            from cryptography.hazmat.backends import default_backend
            load_pem_private_key(private_key.encode(), password=None, backend=default_backend())
            return True
        except Exception as e:
            logger.error(f"Private key validation failed: {str(e)}")
            return False

    def _load_credentials_from_file(self, credentials_path):
        try:
            if not os.path.exists(credentials_path):
                logger.error(f"Credentials file not found: {credentials_path}")
                return None

            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            logger.info("Credentials loaded successfully from file")
            return credentials
        except (ValueError, DefaultCredentialsError) as e:
            logger.error(f"Error loading credentials from file: {str(e)}")
        except PyAsn1Error as e:
            logger.error(f"PyAsn1Error: This might be due to an incorrectly formatted private key. Error: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error loading credentials from file: {e}")
        return None

    def get_transcript(self, recording: AudioRecording, language: str = "en-US") -> str:
        try:
            audio_data = recording.load_recording()
            audio_info = recording.get_audio_info()
            logger.debug(f"Audio info: {audio_info}")
            logger.debug(f"Audio data type: {type(audio_data)}")

            if isinstance(audio_data, bytes):
                audio_bytes = audio_data
            else:
                audio_bytes = audio_data.tobytes()
            audio = sr.AudioData(audio_bytes, audio_info['frame_rate'], audio_info['sample_width'])
            logger.debug(f"Created AudioData object with frame rate: {audio_info['frame_rate']}, sample width: {audio_info['sample_width']}")
            logger.info(f"[AudioTranscriber] Transcribing audio with language: {language}")

            credentials_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
            if not credentials_json:
                logger.error("No Google Cloud credentials available. Unable to perform transcription.")
                return "Transcription unavailable due to missing credentials"

            try:
                credentials_dict = json.loads(credentials_json)
            except json.JSONDecodeError:
                logger.error("Invalid JSON in GOOGLE_APPLICATION_CREDENTIALS_JSON")
                return "Transcription unavailable due to invalid credentials"

            logger.debug("About to call recognize_google_cloud with credentials JSON")
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                json.dump(credentials_dict, temp_file)
                temp_file_path = temp_file.name

            try:
                if audio_info.get('simulated', False):
                    logger.info("[AudioTranscriber] Simulating transcription...")
                    time.sleep(2)
                    simulated_transcript = "This is a simulated transcription. The audio playground is working as expected."
                    logger.info(f"Simulated transcript: {simulated_transcript}")

                    # Call recognize_google_cloud even for simulated transcription
                    self.recognizer.recognize_google_cloud(
                        audio,
                        credentials_json=temp_file_path,
                        language=language
                    )

                    return simulated_transcript
                else:
                    response = self.recognizer.recognize_google_cloud(
                        audio,
                        credentials_json=temp_file_path,
                        language=language
                    )
                logger.debug(f"recognize_google_cloud called successfully. Result: {response}")

                logger.debug(f"Transcription response type: {type(response)}")

                if not response:
                    logger.warning("Empty response received from Google Cloud")
                    return "Could not transcribe the audio"

                if isinstance(response, str):
                    transcript = response
                else:
                    transcript = response.get('results', [{}])[0].get('alternatives', [{}])[0].get('transcript', '')

                if not transcript:
                    logger.warning("No transcript available in the response")
                    return "No transcription available"

                # Process the transcript
                transcript = transcript.strip()  # Remove leading/trailing whitespace
                transcript = transcript.capitalize()  # Capitalize the first letter
                if not transcript.endswith('.'):
                    transcript += '.'  # Add a period if not present

                logger.info(f"Final transcript: {transcript}")
                return transcript

            finally:
                os.unlink(temp_file_path)

        except sr.UnknownValueError:
            logger.warning("Google Cloud Speech could not understand audio")
            return "Audio could not be understood"
        except sr.RequestError as e:
            logger.error(f"Could not request results from Google Cloud Speech service: {e}")
            return f"Error in speech recognition request: {str(e)}"
        except ValueError as e:
            logger.error(f"ValueError occurred during transcription: {e}")
            raise  # Re-raise the ValueError
