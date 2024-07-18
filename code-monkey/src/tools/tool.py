from typing import Dict, Any

class Tool:
    name: str
    description: str
    input_schema: Dict[str, Any]

    def handle_tool_call(self, input: Dict[str, Any]) -> Dict[str, Any] | None:
        raise NotImplementedError("Subclasses must implement handle_tool_call method")