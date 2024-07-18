from tools import copy_src
from agent import ClaudeAgent
# from constants import load_environment

def main() -> None:
    print("Initializing...")
    names = copy_src()
    claude_agent = ClaudeAgent(names)

    print("Go...\n")

    # prompt = "Add tests for token_stats.py, test and fix it."
    # prompt = "Refactor tools.py: 1. Add a new tool class in tool.py. 2. Refactor all tools to be an instance of that class."
    # TODO: Rename "name" prop in tools to "fname".
    prompt = "Fix deps.py: 1. We ast.parse and file.read twice. Refactor it, so it only does that once per file. Cache the results. 2. When reading the file, also compute the file index of each line. 3. The Dependency start and end index should be a file seek index. But currently its just line numbers. Use the newly computed line-to-file-index look-up, as well as the node's start and end colno to compute correct start and end file indexes for Dependency."

    # 3. Each tool should be in its own file inside a new 'tools' folder."
    # prompt = "Run tests for copy_src in tools.py and fix things if they fail."

    claude_agent.run_prompt(prompt)

if __name__ == "__main__":
    main()
