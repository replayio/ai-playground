from tools.utils import copy_src
from agents import Coder
from pprint import pprint
from code_context import CodeContext
# from constants import load_environment

def main() -> None:
    print("Initializing...")
    names = copy_src()
    pprint(names)
    code_context = CodeContext()
    coder = Coder(names)

    print("Go...\n")

    prompt = "1. Modify agents.py: Create a new agents_by_name dict from the agents list."

    # prompt = "Improve tests for deps.py. Run them and fix everything."

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
    coder.run_prompt(prompt)


if __name__ == "__main__":
    main()