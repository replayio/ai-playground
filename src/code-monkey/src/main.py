from tools import copy_src
from agent import ClaudeAgent
# from constants import load_environment

def main() -> None:
    # load_environment()

    print("Initializing...")
    names = copy_src()
    claude_agent = ClaudeAgent(names)

    print("Go...\n")

    # prompt = "Refactor tools.py: 1. Add a new tool class in tool.py. 2. Refactor all tools to be an instance of that class."
    # 3. Each tool should be in its own file inside a new 'tools' folder."
    # prompt = "Run tests for copy_src in tools.py and fix things if they fail."

    claude_agent.run_prompt(prompt)

if __name__ == "__main__":
    main()
