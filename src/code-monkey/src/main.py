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

    prompt = "1. Modify deps.py: Remove get_partial_graph and replace it with a constructor of DependencyGraph that does the same thing. 2. Check result with tests."
    # prompt = "Run tests for copy_src in tools.py and fix things if they fail."

    claude_agent.run_prompt(prompt)

if __name__ == "__main__":
    main()
