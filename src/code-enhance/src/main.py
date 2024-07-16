import os
from typing import List
from anthropic import Anthropic
from tools import (
    AgentName,
    handle_claude_tool_call,
    claude_tools,
    copy_src,
    src_dir,
    artifacts_dir,
    ask_user,
    show_diff
)
from pprint import pprint
from config import OPENAI_API_KEY, ANTHROPIC_API_KEY, MAX_TOKENS


# Prompt Design
SYSTEM_PROMPT = """
1. Your max_tokens are {MAX_TOKENS}. If any assistant message might exceed the token limit, don't try and respond negatively with an explanation instead.
2. Prefix negative responses with "❌". Prefix responses that indicate a significant success with "✅". Don't prefix neutral responses.
3. Use tools only if necessary.
4. Prefer using replace_in_file over write_file.
5. Don't make white-space-only changes to files.
6. If you have low confidence in a response or don't understand an instruction, explain why and use the ask_user tool to gather clarifications.
"""

# Agents


class Agent:
    name: AgentName
    names: List[str]

    def __init__(self, names: List[str]) -> None:
        self.names = names

    def run_prompt(self, prompt: str) -> str:
        raise NotImplementedError("Subclasses must implement run_prompt method")

    def imbue_prompt(self, query: str) -> str:
        # These are all files: {self.names}. Only if you need to, read or write them with tools. Don't explain your actions.
        return f"""
These are all files: {self.names}.
Query: {query}
    """.strip()


class ClaudeAgent(Agent):
    name = AgentName.Claude

    def __init__(self, names: List[str]) -> None:
        super().__init__(names)
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)

    def run_prompt(self, prompt: str) -> str:
        prompt = prompt.strip()
        print(f'Q: "{prompt}"')
        prompt = self.imbue_prompt(prompt)
        messages = [{"role": "user", "content": prompt}]

        more = True
        had_any_text = False
        modified_files = set()
        while more:
            response = self.client.messages.create(
                temperature=0,
                system=SYSTEM_PROMPT,
                model="claude-3-5-sonnet-20240620",
                max_tokens=MAX_TOKENS,
                messages=messages,
                tools=claude_tools,
                extra_headers={"anthropic-beta": "max-tokens-3-5-sonnet-2024-07-15"},
            )
            assistant_messages = []
            user_messages = []

            for response_message in response.content:
                assistant_messages.append(response_message)

                if response_message.type == "tool_use":
                    user_messages.append(
                        handle_claude_tool_call(
                            self.name,
                            response_message.id,
                            response_message.name,
                            response_message.input,
                            modified_files,
                        )
                    )
                elif response_message.type == "text":
                    had_any_text = True
                    print(f"A: {response_message.text}")
                elif response_message.type == "error":
                    had_any_text = True
                    return f"ERROR: {response_message.text}"
                elif response_message.type == "final":
                    had_any_text = True
                    return f"DONE: {str(response_message)}"
                else:
                    raise Exception(
                        f"Unhandled message type: {response_message.type} - {str(response_message)}"
                    )
            if len(user_messages) == 0:
                # No more replies: Done!
                more = False
            else:
                messages.append({"role": "assistant", "content": assistant_messages})
                messages.append({"role": "user", "content": user_messages})

        if not had_any_text:
            print("Done.")

        if modified_files:
            print(f"Modified files: {', '.join(modified_files)}")
            for file in modified_files:
                original_file = os.path.join(src_dir, file)
                modified_file = os.path.join(artifacts_dir, file)
                diff = show_diff(original_file, modified_file)
                print(f"Diff for {file}:")
                print(diff)

                apply_changes = ask_user(
                    f"Do you want to apply the changes to {file}? (Y/n): "
                ).lower()
                if apply_changes == "Y" or apply_changes == "":
                    with open(modified_file, "r") as modified:
                        content = modified.read()
                    with open(original_file, "w") as original:
                        original.write(content)
                    print(f"✅ Changes applied to {file}")
                else:
                    print(f"❌ Changes not applied to {file}")


def main() -> None:
    print("Initializing...")
    # openai_agent = OpenAIAgent()
    names = copy_src()
    claude_agent = ClaudeAgent(names)
    # names = []

    print("Go...\n")

    prompt = "Modify "

    # prompt = "What is the end index of tools.py? Is the end index of tools.py different from its length? Also print the numerical confidence you have in your answer."
    # prompt = "What are the last 100 characters of tools.py?"

    # prompt = "Append a hello_world function to the end of tools.py"
    # prompt = "What is your max_tokens setting?"
    # prompt = "Modify tools.py: Add an ask_user tool. The tool should use stdio to ask the user. The user's input is returned to the assistant."
    # prompt = "Modify tools.py: Modify the write_file tool: 1. rename write_file to edit_file. 2. take optional start and end parameters that replace the characters between start and end with the provided new content."
    # prompt = "Modify test.py: Add a snake program into it using pygame"
    # prompt = "If you had to modify tools.py, what parameters would you pass to the write_file tool?"
    claude_agent.run_prompt(prompt)

    # print("\n\n")

    # prompt = "Write a hello world program into main.py."
    # claude_agent.run_prompt(prompt)

    # print("\n\n")

    # prompt = "Summarize the contents of main.py."
    # claude_agent.run_prompt(prompt)


if __name__ == "__main__":
    main()
