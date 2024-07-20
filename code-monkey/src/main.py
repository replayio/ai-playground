from agent import ClaudeAgent
from agents import make_coder
from pprint import pprint
from code_context import CodeContext
# from constants import load_environment

def main() -> None:
    print("Initializing...")

    code_context = CodeContext()
    code_context.copy_src()

    Coder = make_coder(ClaudeAgent)
    coder = Coder(code_context)

    print("Go...\n")

    # prompt = "Improve tests for deps.py. Run them and fix everything."

    # TODO:
    # "1. Add a new abstract CodeAnalysisTool class to the tools folder. Make sure it is implemented just like IOTool, and inherits from Tool. 2. Have GetDependenciesTool inherit from it. 3. Fix the GetDependenciesTool to call a new function on the graph that returns an adjacency list format of all imports and imported_by's of the given modules."

    # TODO:

    # TODO:
    # prompt = "Add a FindDependenciesTool: Given a dependency_name, return all dependencies (and their modules) that contain that string."

    # TODO:
    # prompt = "Fix artifacts_dir: 1. Use get_dependencies to find all dependencies of it."

    # TODO:
    # prompt = "Run tests for copy_src in tools.py and fix things if they fail."

    coder.run_prompt(prompt)


if __name__ == "__main__":
    main()