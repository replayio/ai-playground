import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import load_environment

from audio_recording import AudioRecording
from audio_transcriber import AudioTranscriber

this_dir = os.path.dirname(os.path.abspath(__file__))


def main():
    print("Welcome to the Audio Playground!")
    print("This script will record your voice and transcribe it.")

    load_environment()

    recording = AudioRecording(os.path.join(this_dir, "playground_recording.wav"))

    print("Press 'ENTER' to start recording...")
    input()

    print("Recording started. Press 'ENTER' to stop...")
    recording.start_recording()

    input()
    recording.stop_recording()
    print("Recording stopped.")

    print("Transcribing...")
    transcriber = AudioTranscriber()
    transcript = transcriber.get_transcript(recording)

    print("\nTranscription result:")
    print(transcript)

    print("\nThank you for using Audio Playground!")


if __name__ == "__main__":
    main()
