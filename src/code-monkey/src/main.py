from tools import copy_src
from agent import ClaudeAgent
from constants import ANTHROPIC_API_KEY

def main() -> None:
    if not ANTHROPIC_API_KEY:
        raise ValueError(
            "API keys not found. Please check your .env and .secret.env files."
        )
    print("Initializing...")
    names = copy_src()
    claude_agent = ClaudeAgent(names)

    print("Go...\n")

    prompt = "Add a default execution block to deps.py that will print the default graph."
    # prompt = "Run tests for copy_src in tools.py and fix things if they fail."

    claude_agent.run_prompt(prompt)

if __name__ == "__main__":
    main()
