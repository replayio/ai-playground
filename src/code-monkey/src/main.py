from tools import copy_src
from agent import ClaudeAgent

def main() -> None:
    print("Initializing...")
    names = copy_src()
    claude_agent = ClaudeAgent(names)

    print("Go...\n")

    # prompt = "Fix the exec tool in tools.py: Remember all previously approved exec calls. If the user approved them in the past, don't check again."
    prompt = "Run deps.py and fix it if it does not work."
    # prompt = "Use the exec tool to execute uml.py."
    # prompt = "Modify uml.py: use pyreverse instead of astroid."
    # prompt = "Run tests for copy_src in tools.py and fix things if they fail."

    claude_agent.run_prompt(prompt)

if __name__ == "__main__":
    main()
