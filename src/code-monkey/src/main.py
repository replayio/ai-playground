from tools.utils import copy_src
from agent import ClaudeAgent
# from constants import load_environment

def main() -> None:
    print("Initializing...")
    names = copy_src()
    claude_agent = ClaudeAgent(names)

    print("Go...\n")

    # prompt = "Fix main.py comments"
    prompt = ""

    # prompt = "Split classes from tools.py into multiple files: 0. Add all files to a new tools folder. 1. Add a new tool.py that contains the Tool class. 2. Create one file for each sub-class. 3. Use ask_user if there are any issues with code quality or complexity."

    claude_agent.run_prompt(prompt)

if __name__ == "__main__":
    main()
