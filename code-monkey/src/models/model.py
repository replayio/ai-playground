from enum import StrEnum
from agents.base_agent import BaseAgent

class ModelName(StrEnum):
    Noop = "noop"
    OpenAI = "openai"
    Anthropic = "anthropic"

class Model:
    name: ModelName
    agent: BaseAgent

    def __init__(self):
        pass

    def run_prompt(self, prompt: str) -> str:
        raise NotImplementedError("Subclasses must implement run_prompt method")
    