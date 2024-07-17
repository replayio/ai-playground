from tools import copy_src
from agent import ClaudeAgent

def main() -> None:
    print("Initializing...")
    names = copy_src()
    claude_agent = ClaudeAgent(names)

    print("Go...\n")

    prompt = "Create a new file uml.py that generates a uml diagram of all files in constant.py's src_dir folder (recursively)."
    # prompt = "Run tests for copy_src in tools.py and fix things if they fail."

    claude_agent.run_prompt(prompt)

if __name__ == "__main__":
    main()
