import os
from enum import StrEnum
from typing import List, Tuple, Set
from anthropic import Anthropic
from anthropic.types import Message, MessageParam
from tools.tools import get_tool_specs, handle_tool_call
from token_stats import TokenStats
from pprint import pprint
from agents.base_agent import BaseAgent
from instrumentation import current_span, instrument
from .model import Model, ModelName
from .registry import register_model_service
from .msn import parse_msn

# See: https://console.anthropic.com/settings/cost
DEFAULT_MSN="anthropic/claude-3-5-sonnet-20240620/anthropic-beta=max-tokens-3-5-sonnet-2024-07-15"
MAX_TOKENS = 8192

class EnvVars(StrEnum):
    API_KEY = "ANTHROPIC_API_KEY"
    MAX_TOKENS = "MAX_TOKENS"

def get_max_tokens():
    return int(os.getenv(EnvVars.MAX_TOKENS) or 1000)


# SELECTED_MODEL = "claude-3-sonnet-20240229"
# EXTRA_HEADERS = None
# MAX_TOKENS = 4096

class AnthropicModel(Model):
    name = ModelName.Anthropic

    @instrument("Model.__init__", attributes={"service": "Anthropic" })
    def __init__(self, agent: BaseAgent, msn: str | None = None) -> None:
        super().__init__()

        api_key = os.getenv(EnvVars.API_KEY)
        if not api_key:
            raise Exception(
                f"API Key was not defined. Make sure {EnvVars.API_KEY} is in your .env.secret file"
            )

        self.agent = agent

        if msn is None:
            msn = DEFAULT_MSN
        [ _, model, extra_flags ] = parse_msn(msn)
        print(f"AnthropicModel: model={model}, extra_flags={extra_flags}")
        self.client = Anthropic(api_key=api_key)
        self.selected_model = model
        self.extra_headers = extra_flags
        self.token_stats = TokenStats()

    @instrument("Model.run_prompt", attributes={"service": "Anthropic" })
    def run_prompt(self, prompt: str) -> str:
        current_span().set_attribute("prompt", prompt)

        prompt = self.agent.prepare_prompt(prompt)
        modified_files = set()
        had_any_text = False
        assistant_messages = []
        user_messages = [{"role": "user", "content": prompt}]
        messages = user_messages
        final_message_content = ""

        try:
            while True:
                # XXX(toshok) number of messages (and number of _bytes_ probably) to honeycomb
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
        finally:
            self.token_stats.print_stats()

        current_span().set_attribute("final_message_content", final_message_content)
        return final_message_content

    @instrument("Claude._get_claude_response", attributes={"service": "Anthropic" })
    def _get_claude_response(self, messages: List[MessageParam]) -> Message:
        self.token_stats.check_rate_limit()
        try:
            response = self.client.messages.create(
                temperature=0,
                system=self.agent.get_system_prompt(),
                model=self.selected_model,
                max_tokens=get_max_tokens(),
                messages=messages,
                tools=get_tool_specs(self.agent.get_tools()),
                extra_headers=self.extra_headers,
            )
            current_span().set_attributes({
                "input_messages": str(messages),
                "response_content": str(response.content),
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            })
            return response
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
        import logging
        logger = logging.getLogger(__name__)
        final_message_content = ""
        for response_message in response.content:
            logger.debug(f"Processing response message: {response_message}")
            assistant_messages.append(response_message)

            if response_message.type == "tool_use":
                logger.debug(f"Tool used: {response_message.name}")
                tool_result = self._handle_tool_use(response_message, modified_files)
                user_messages.append(tool_result)
                logger.debug(f"Tool result summary: {tool_result['content'][:100] if isinstance(tool_result['content'], str) else ""}...")
            elif response_message.type == "text":
                had_any_text = True
                final_message_content = response_message.text
                print(f"A: {final_message_content}")
            elif response_message.type == "error":
                had_any_text = True
                final_message_content = response_message.text
                print(f"ERROR: {final_message_content}")
                logger.debug(f"Error encountered: {final_message_content}")
                return had_any_text, final_message_content
            elif response_message.type == "final":
                had_any_text = True
                final_message_content = str(response_message)
                print(f"DONE: {final_message_content}")
                logger.debug(f"Final message: {final_message_content}")
                return had_any_text, final_message_content
            else:
                error_msg = f"Unhandled message type: {response_message.type} - {str(response_message)}"
                logger.debug(f"Error: {error_msg}")
                raise Exception(error_msg)

        return had_any_text, final_message_content

    def _handle_tool_use(
        self, response_message: dict, modified_files: Set[str]
    ) -> dict:
        tool_name: str = response_message.name
        tool = self.agent.get_tool(tool_name)
        if tool is None:
            raise Exception(f"Unknown tool: {tool_name}")

        return handle_tool_call(
            response_message.id,
            response_message.input,
            modified_files,
            tool,
        )

    def _handle_completion(self, had_any_text: bool, modified_files: Set[str]) -> bool:
        return self.agent.handle_completion(had_any_text, modified_files)


register_model_service(ModelName.Anthropic, AnthropicModel)