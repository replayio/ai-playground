from tools import copy_src
from agent import ClaudeAgent
# from constants import load_environment

def main() -> None:
    print("Initializing...")
    names = copy_src()
    claude_agent = ClaudeAgent(names)

    print("Go...\n")

    # prompt = "Add tests for token_stats.py, test and fix it."
    prompt = "Don't create files unless you have to. Refactor tools.py: 1. Add a new Tool class in tool.py. 2. Refactor all tools to have their own class, inheriting from Tool. Keep all tool-specific logic to the tool object. 3. In handle_claude_tool_call, for each tool use, create an instance of the respective Tool class."

    # 3. Each tool should be in its own file inside a new 'tools' folder."
    # prompt = "Run tests for copy_src in tools.py and fix things if they fail."

    claude_agent.run_prompt(prompt)

if __name__ == "__main__":
    main()
