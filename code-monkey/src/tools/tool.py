from typing import Dict, Any
from abc import ABC, abstractmethod
from tool_user import BaseAgent

class Tool(ABC):
    name: str
    agent: BaseAgent
    description: str
    input_schema: Dict[str, Any]

    def __init__(self, agent: BaseAgent):
        self.agent = agent

    @abstractmethod
    def handle_tool_call(self, input: Dict[str, Any]) -> Dict[str, Any] | None:
        raise NotImplementedError("Subclasses must implement handle_tool_call method")
