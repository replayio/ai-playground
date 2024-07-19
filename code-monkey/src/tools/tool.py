from typing import Dict, Any
from abc import ABC, abstractmethod

class Tool(ABC):
    name: str
    description: str
    input_schema: Dict[str, Any]

    @abstractmethod
    def handle_tool_call(self, input: Dict[str, Any]) -> Dict[str, Any] | None:
        pass