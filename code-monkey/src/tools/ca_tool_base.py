from typing import Dict, Any

class CATool:
    name = "ca_tool_base"
    description = "Base class for CA tools"
    input_schema = {
        "type": "object",
        "properties": {},
        "required": []
    }

    def __init__(self):
        pass

    def handle_tool_call(self, input: Dict[str, Any]) -> str:
        raise NotImplementedError("This method should be implemented by subclasses.")
