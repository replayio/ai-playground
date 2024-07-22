import os
from typing import List, Tuple
from anthropic import Anthropic
from anthropic.types import Message, MessageParam
from tools.tools import ModelName, get_tool_specs, handle_claude_tool_call
from token_stats import TokenStats
from pprint import pprint
from agents.base_agent import BaseAgent

from typing import Set

# See: https://console.anthropic.com/settings/cost
SELECTED_MODEL = "claude-3-5-sonnet-20240620"
EXTRA_HEADERS = {"anthropic-beta": "max-tokens-3-5-sonnet-2024-07-15"}
MAX_TOKENS = 8192

def get_api_key():
    return os.getenv("ANTHROPIC_API_KEY")

def get_max_tokens():
    return int(os.getenv("MAX_TOKENS") or 1000)


# SELECTED_MODEL = "claude-3-sonnet-20240229"
# EXTRA_HEADERS = None
# MAX_TOKENS = 4096


class Model:
    name: ModelName
    agent: BaseAgent

    def __init__(self):
        pass

    def run_prompt(self, prompt: str) -> str:
        raise NotImplementedError("Subclasses must implement run_prompt method")


class Claude(Model):
    name = ModelName.Claude

    def __init__(self, agent: BaseAgent) -> None:
        self.agent = agent
        if not get_api_key():
            raise Exception(
                "get_api_key() was not defined. Check your .env.secret file"
            )
        super().__init__()
        self.client = Anthropic(api_key=get_api_key())
        self.token_stats = TokenStats()

    def run_prompt(self, prompt: str) -> str:
        prompt = self.agent.prepare_prompt(prompt)
        modified_files = set()
        had_any_text = False
        assistant_messages = []
        user_messages = [{"role": "user", "content": prompt}]
        messages = user_messages
        final_message_content = ""

        try:
            while True:
                response = self._get_claude_response(messages)
                self.token_stats.update(
                    response.usage.input_tokens,
                    response.usage.output_tokens,
                    response.content,
                )
                assistant_messages = []
                user_messages = []

                # Debug-print stats
                self.token_stats.print_stats()

                had_any_text, final_message_content = self._process_response(
                    response,
                    modified_files,
                    had_any_text,
                    assistant_messages,
                    user_messages,
                )

                if not len(user_messages):
                    # We are done when no more input is given to the assistant.
                    if self._handle_completion(had_any_text, modified_files):
                        break

                messages.extend(
                    [
                        {"role": "assistant", "content": assistant_messages},
                        {"role": "user", "content": user_messages},
                    ]
                )
        except Exception as err:
            self.token_stats.print_stats()
            raise err

        self.token_stats.print_stats()
        return final_message_content

    def _get_claude_response(self, messages: List[MessageParam]) -> Message:
        self.token_stats.check_rate_limit()
        try:
            return self.client.messages.create(
                temperature=0,
                system=self.agent.get_system_prompt(),
                model=SELECTED_MODEL,
                max_tokens=get_max_tokens(),
                messages=messages,
                tools=get_tool_specs(self.agent.get_tools()),
                extra_headers=EXTRA_HEADERS,
            )
        except Exception as err:
            print("##########################################################")
            print("PROMPT ERROR with the following messages:")
            pprint(messages)
            print("##########################################################")
            raise err

    def _process_response(
        self,
        response: Message,
        modified_files: set,
        had_any_text: bool,
        assistant_messages: List[dict],
        user_messages: List[dict],
    ) -> Tuple[bool, str]:
        final_message_content = ""
        for response_message in response.content:
            # print("RAW RESPONSE:")
            # pprint(response_message)
            assistant_messages.append(response_message)

            if response_message.type == "tool_use":
                user_messages.append(
                    self._handle_tool_use(response_message, modified_files)
                )
            elif response_message.type == "text":
                had_any_text = True
                final_message_content = response_message.text
                print(f"A: {final_message_content}")
            elif response_message.type == "error":
                had_any_text = True
                final_message_content = response_message.text
                print(f"ERROR: {final_message_content}")
                return had_any_text, final_message_content
            elif response_message.type == "final":
                had_any_text = True
                final_message_content = str(response_message)
                print(f"DONE: {final_message_content}")
                return had_any_text, final_message_content
            else:
                raise Exception(
                    f"Unhandled message type: {response_message.type} - {str(response_message)}"
                )

        return had_any_text, final_message_content

    def _handle_tool_use(
        self, response_message: dict, modified_files: Set[str]
    ) -> dict:
        tool_name: str = response_message.name
        tool = self.agent.get_tool(tool_name)
        if tool is None:
            raise Exception(f"Unknown tool: {tool_name}")

        return handle_claude_tool_call(
            response_message.id,
            response_message.input,
            modified_files,
            tool,
        )

    def _handle_completion(self, had_any_text: bool, modified_files: Set[str]) -> bool:
        return self.agent.handle_completion(had_any_text, modified_files)
