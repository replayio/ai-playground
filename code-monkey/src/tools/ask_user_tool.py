from typing import Dict, Any
from .tool import Tool
from instrumentation import instrument

class AskUserTool(Tool):
    name = "ask_user"
    description = "Ask the user a question and return their response"
    input_schema = {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "The prompt to show the user",
            }
        },
        "required": ["prompt"],
    }

    @instrument("handle_tool_call", attributes={ "tool": "AskUserTool" })
    def handle_tool_call(self, input: Dict[str, Any]) -> Dict[str, Any] | None:
        prompt = input["prompt"]
        print(prompt)
        response = input()
        return response