from typing import Dict, List, Any, Type
from abc import ABC, abstractmethod

class Tool(ABC):
    name: str
    description: str
    input_schema: Dict[str, Any]

    @abstractmethod
    def handle_tool_call(self, input: Dict[str, Any]) -> Dict[str, Any] | None:
        raise NotImplementedError("Subclasses must implement handle_tool_call method")


class ToolSpec:
    def __init__(self, tool_class: Type[Tool], tool_args: List[Any]):
        self.tool_class = tool_class
        self.tool_args = tool_args
