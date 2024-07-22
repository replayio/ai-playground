import sys
import os
import time
import keyboard  # Using the keyboard module to detect key presses
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

        print("Press 'r' to start recording...")
        while True:
            if keyboard.is_pressed('r'):
                break

        print("Recording started. Press 's' to stop...")
        recording.start_recording()

        while True:
            if keyboard.is_pressed('s'):
                recording.stop_recording()
                print("Recording stopped.")
                break

        print("Transcribing...")
        transcriber = AudioTranscriber()
        transcript = transcriber.get_transcript(recording)

        print("\nTranscription result:")
        print(transcript)

    print("\nThank you for using Audio Playground!")

if __name__ == "__main__":
    main()
