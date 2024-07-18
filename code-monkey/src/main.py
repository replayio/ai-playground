from tools.utils import copy_src
from agent import ClaudeAgent
from pprint import pprint
# from constants import load_environment

def main() -> None:
    print("Initializing...")
    names = copy_src()
    pprint(names)
    claude_agent = ClaudeAgent(names)

    print("Go...\n")

    # prompt = "Fix main.py comments"
    # prompt = "Add a test for the RGTool."

    # prompt = "Split classes from tools.py into multiple files: 0. Add all files to a new tools folder. 1. Add a new tool.py that contains the Tool class. 2. Create one file for each sub-class. 3. Use ask_user if there are any issues with code quality or complexity."

    prompt = "Fix copy_src to ignore everything from <ROOT_DIRECTORY>/.gitignore, where ROOT_DIRECTORY is two folders up from itself."
    claude_agent.run_prompt(prompt)

    # prompt = "Fix deps.py: 1. If any dependency graph is queried, just read and parse all files, and construct the full dependency graph. 2. Merge get_imports and get_top_level_constructs to a new function find_dependencies that just returns List[Dependency]. 3. Add a new imported_by lookup table and a corresponding get_imported_by(dep_name) function."

    # TODO:
    # prompt = "Fix the GetDependenciesTool to call a new function on the graph that returns an adjacency list format of all imports and imported_by's of the given modules."

    # TODO:

    # TODO:
    # prompt = "Add a FindDependenciesTool: Given a dependency_name, return all dependencies (and their modules) that contain that string."

    # prompt = "Add tests for token_stats.py, test and fix it."

    # TODO:
    # prompt = "Fix artifacts_dir: 1. Use get_dependencies to find all dependencies of it."

    # TODO:
    # prompt = "Run tests for copy_src in tools.py and fix things if they fail."


if __name__ == "__main__":
    main()
