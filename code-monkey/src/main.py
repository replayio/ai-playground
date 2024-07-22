
from agents.agents import Coder
from constants import load_environment

def main() -> None:
    print("Initializing...")

    load_environment()

    coder = Coder()
    coder.initialize()

    print("Go...\n")

    prompt = "Summarize test.py."
    coder.run_prompt(prompt)


if __name__ == "__main__":
    main()
