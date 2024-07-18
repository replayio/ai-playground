import os
from typing import List
from anthropic import Anthropic
from anthropic.types import Message
from tools import (
    AgentName,
    handle_claude_tool_call,
    claude_tools,
    ask_user,
    show_diff,
    src_dir,
    artifacts_dir,
)
from constants import ANTHROPIC_API_KEY, MAX_TOKENS, SYSTEM_PROMPT
from token_stats import TokenStats
from pprint import pprint

class Agent:
    name: AgentName
    names: List[str]

    def __init__(self, names: List[str]) -> None:
        self.names = names

    def run_prompt(self, prompt: str) -> str:
        raise NotImplementedError("Subclasses must implement run_prompt method")

    def imbue_prompt(self, query: str) -> str:
        return f"""
These are all files: {self.names}.
Query: {query}
    """.strip()


class ClaudeAgent(Agent):
    name = AgentName.Claude

    def __init__(self, names: List[str]) -> None:
        super().__init__(names)
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.token_stats = TokenStats()

    def run_prompt(self, prompt: str) -> str:
        prompt = self._prepare_prompt(prompt)
        messages = [{"role": "user", "content": prompt}]
        modified_files = set()
        had_any_text = False
        assistant_messages = []
        user_messages = []

        while True:
            response = self._get_claude_response(messages)
            self.token_stats.update(response.usage.input_tokens, response.usage.output_tokens)
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

        self.token_stats.print_stats()

    def _prepare_prompt(self, prompt: str) -> str:
        prompt = prompt.strip()
        print(f'Q: "{prompt}"')
        return self.imbue_prompt(prompt)

    def _get_claude_response(self, messages: List[dict]) -> Message:
        self.token_stats.check_rate_limit()
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

    def _process_response(self, response: Message, modified_files: set, had_any_text: bool, assistant_messages: List[dict], user_messages: List[dict]) -> bool:
        for response_message in response.content:
            print("RAW RESPONSE:")
            pprint(response_message)
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
        return True

    def _handle_modified_file(self, file: str) -> None:
        original_file = os.path.join(src_dir, file)
        modified_file = os.path.join(artifacts_dir, file)
        show_diff(original_file, modified_file)
        apply_changes = ask_user(f"Do you want to apply the changes to {file} (diff shown in VSCode)? (Y/n): ").lower()
        if apply_changes == "y" or apply_changes == "":
            self._apply_changes(original_file, modified_file)
            print(f"✅ Changes applied to {file}")
        else:
            print(f"❌ Changes not applied to {file}")

    def _apply_changes(self, original_file: str, modified_file: str) -> None:
        with open(modified_file, "r") as modified, open(original_file, "w") as original:
            original.write(modified.read())