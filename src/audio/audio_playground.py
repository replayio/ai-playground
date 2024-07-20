import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio_input import AudioInput

def main():
    audio_input = AudioInput()

    print("Welcome to the Audio Playground!")
    print("This script will record your voice and transcribe it.")
    print("You can test the functionality multiple times.")

    while True:
        print("\nPress Enter to start recording (or type 'exit' to quit)...")
        user_choice = input()

        if user_choice.lower() == 'exit':
            break

        print("Recording... Press Enter to stop.")
        transcribed_text = audio_input.get_input()

        print(f"\nTranscribed text: {transcribed_text}")

    print("Thank you for using Audio Playground!")

if __name__ == "__main__":
    main()
