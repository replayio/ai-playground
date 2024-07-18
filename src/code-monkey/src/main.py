from tools import copy_src
from agent import ClaudeAgent
# from constants import load_environment

def main() -> None:
    print("Initializing...")
    names = copy_src()
    claude_agent = ClaudeAgent(names)

    print("Go...\n")


    prompt = "Split classes from tools.py into multiple files: 0. Add all files to a new tools folder. 1. Add a new tool.py that contains the Tool class. 2. Create one file for each sub-class."
    # prompt = "Add a FindDependenciesTool: Given a dependency_name, return all dependencies (and their modules) that contain that string."

    # prompt = "Add tests for token_stats.py, test and fix it."

    # TODO:
    # prompt = "Fix artifacts_dir: 1. Use get_dependencies to find all dependencies of it."

    # TODO:
    # prompt = "Run tests for copy_src in tools.py and fix things if they fail."

    claude_agent.run_prompt(prompt)

if __name__ == "__main__":
    main()
