from abc import ABC, abstractmethod
from langchain_core.tools import BaseTool
from typing import List


class BaseAgent(ABC):
    tools: List[BaseTool] = None
    SYSTEM_PROMPT = "You don't know what to do. Tell the user that they can't use you and must use an agent with a proper SYSTEM_PROMPT instead."

    @abstractmethod
    def run_prompt(self, prompt: str) -> str:
        pass

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    @abstractmethod
    def prepare_prompt(self, prompt: str) -> str:
        pass

    @abstractmethod
    def handle_completion(self, had_any_text: bool, modified_files: set) -> None:
        pass
