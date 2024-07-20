import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import load_environment

from audio_recording import AudioRecording
from audio_transcriber import AudioTranscriber

def main():
    print("Welcome to the Audio Playground!")
    print("This script will record your voice and transcribe it.")

    load_environment()

    if not os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
        print("Warning: GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")
        print("Transcription will not be possible without valid credentials.")
        print("Please set the environment variable with the path to your Google Cloud service account key file.")

    try:
        recording = AudioRecording()

        input("Press Enter to start recording...")
        print("Recording started. Speak now...")
        recording.start_recording()

        time.sleep(5)  # Record for 5 seconds

        print("Recording stopped.")
        recording.stop_recording()

        print("Transcribing...")
        transcriber = AudioTranscriber()
        transcript = transcriber.get_transcript(recording)

        print("\nTranscription result:")
        print(transcript)
    except FileNotFoundError as e:
        print(f"Error: Unable to open the audio file. {str(e)}")
    except ValueError as e:
        if "credentials" in str(e).lower():
            print("Error: Unable to authenticate with Google Cloud.")
            print("Please ensure that the GOOGLE_APPLICATION_CREDENTIALS environment variable is set correctly.")
        else:
            print(f"An unexpected ValueError occurred: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

    print("\nThank you for using Audio Playground!")

if __name__ == "__main__":
    main()
