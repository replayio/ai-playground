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
from config import ANTHROPIC_API_KEY, MAX_TOKENS, SYSTEM_PROMPT


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
        prompt = self._prepare_prompt(prompt)
        messages = [{"role": "user", "content": prompt}]
        modified_files = set()
        had_any_text = False
        assistant_messages = []
        user_messages = []

        while True:
            response = self._get_claude_response(messages)
            had_any_text = self._process_response(response, modified_files, had_any_text, assistant_messages, user_messages)
            
            if not len(user_messages):
                # We are done when no more input is given to the assistant.
                if self._handle_completion(had_any_text, modified_files):
                    break

            messages.extend([
                {"role": "assistant", "content": assistant_messages},
                {"role": "user", "content": user_messages}
            ])
            assistant_messages = []
            user_messages = []

    def _prepare_prompt(self, prompt: str) -> str:
        prompt = prompt.strip()
        print(f'Q: "{prompt}"')
        return self.imbue_prompt(prompt)

    def _get_claude_response(self, messages: List[dict]) -> dict:
        try:
            return self.client.messages.create(
                temperature=0,
                system=SYSTEM_PROMPT,
                model="claude-3-5-sonnet-20240620",
                max_tokens=MAX_TOKENS,
                messages=messages,
                tools=claude_tools,
                extra_headers={"anthropic-beta": "max-tokens-3-5-sonnet-2024-07-15"},
            )
        except Exception as err:
            print("PROMPT ERROR with the following messages:")
            pprint(messages)
            raise err

    def _process_response(self, response: dict, modified_files: set, had_any_text: bool, assistant_messages: List[dict], user_messages: List[dict]) -> bool:
        for response_message in response.content:
            assistant_messages.append(response_message)

            if response_message.type == "tool_use":
                user_messages.append(self._handle_tool_use(response_message, modified_files))
            elif response_message.type == "text":
                had_any_text = True
                print(f"A: {response_message.text}")
            elif response_message.type == "error":
                had_any_text = True
                print(f"ERROR: {response_message.text}")
                return had_any_text
            elif response_message.type == "final":
                had_any_text = True
                print(f"DONE: {str(response_message)}")
                return had_any_text
            else:
                raise Exception(f"Unhandled message type: {response_message.type} - {str(response_message)}")

        return had_any_text

    def _handle_tool_use(self, response_message: dict, modified_files: set) -> dict:
        return handle_claude_tool_call(
            self.name,
            response_message.id,
            response_message.name,
            response_message.input,
            modified_files,
        )

    def _handle_completion(self, had_any_text: bool, modified_files: set) -> None:
        if not had_any_text:
            print("Done.")

        if modified_files:
            print(f"Modified files: {', '.join(modified_files)}")
            for file in modified_files:
                self._handle_modified_file(file)

    def _handle_modified_file(self, file: str) -> None:
        original_file = os.path.join(src_dir, file)
        modified_file = os.path.join(artifacts_dir, file)
        diff = show_diff(original_file, modified_file)
        print(f"Diff for {file}:")
        print(diff)

        apply_changes = ask_user(f"Do you want to apply the changes to {file}? (Y/n): ").lower()
        if apply_changes == "y" or apply_changes == "":
            self._apply_changes(original_file, modified_file)
            print(f"✅ Changes applied to {file}")
        else:
            print(f"❌ Changes not applied to {file}")

    def _apply_changes(self, original_file: str, modified_file: str) -> None:
        with open(modified_file, "r") as modified, open(original_file, "w") as original:
            original.write(modified.read())


def main() -> None:
    print("Initializing...")
    names = copy_src()
    claude_agent = ClaudeAgent(names)
    # names = []

    print("Go...\n")

    prompt = "In tools.py: Add and hook up a run_test tool. It should spawn a process to run Python tests in a given file. File name should work like in the other file tools. The tool should provide the test result and stdout and stderr back to the agent. It should also show the test results to the user."

    claude_agent.run_prompt(prompt)

if __name__ == "__main__":
    main()
