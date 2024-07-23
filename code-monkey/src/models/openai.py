import os
from openai import OpenAI
from enum import StrEnum
from typing import List, Tuple, Set
from agents.base_agent import BaseAgent
from tools.tools import get_tool_specs, handle_tool_call
from token_stats import TokenStats
from instrumentation import current_span, instrument
from .model import Model, ModelName
from .registry import register_model_service
from .msn import parse_msn


class EnvVars(StrEnum):
    API_KEY = "OPENAI_API_KEY"


DEFAULT_MSN = "openai/gpt-3.5-turbo"

class OpenAIModel(Model):
    name = ModelName.OpenAI

    @instrument("Model.__init__", attributes={"service": "OpenAI", "model": "GPT" })
    def __init__(self, agent: BaseAgent, msn: str | None = None) -> None:
        super().__init__()

        api_key = os.getenv(EnvVars.API_KEY)
        if not api_key:
            raise Exception(
                f"API Key was not defined. Make sure {EnvVars.API_KEY} is in your .env.secret file"
            )

        if msn is None:
            msn = DEFAULT_MSN
        [ _, model, extra_flags ] = parse_msn(msn)
        print(f"OpenAIModel: model={model}, extra_flags={extra_flags}")
        self.agent = agent
        self.client = OpenAI(api_key=api_key)
        self.token_stats = TokenStats()

    @instrument("Model.run_prompt", attributes={"service": "OpenAI", "model": "GPT" })
    def run_prompt(self, prompt: str) -> str:
        raise NotImplementedError()

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

register_model_service(ModelName.OpenAI, OpenAIModel)
