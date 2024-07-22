from typing import Dict, Any
from .io_tool import IOTool
from .utils import make_file_path

class ReadFileTool(IOTool):
    name = "read_file"
    description = "Read the contents of the file of given name"
    input_schema = {
        "type": "object",
        "properties": {
            "fname": {"type": "string"},
        },
        "required": ["fname"],
    }

    def handle_tool_call(self, input: Dict[str, Any]) -> str | None:
        name = input["fname"]
        file_path = make_file_path(name)
        with open(file_path, "r") as file:
            content = file.read()
        return content
