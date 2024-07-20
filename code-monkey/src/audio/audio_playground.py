import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import load_environment

from audio_recording import AudioRecording
from audio_transcriber import AudioTranscriber

def main():
    print("Welcome to the Audio Playground!")
    print("This script will transcribe the test audio file.")

    load_environment()

    if not os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
        raise Exception("Warning: GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")

    try:
        recording = AudioRecording()
        audio_data = recording.load_recording()

        print(f"[DEBUG] Audio data loaded. Length: {len(audio_data)} samples")

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
