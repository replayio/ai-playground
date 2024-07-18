import os
from typing import Dict, Any
from .io_tool import IOTool
from .utils import make_file_path

class WriteFileTool(IOTool):
    name = "write_file"
    description = "Write content to the file of given name"
    input_schema = {
        "type": "object",
        "properties": {
            "fname": {"type": "string", "description": "Name of the file to edit."},
            "content": {
                "type": "string",
                "description": "New contents of the file.",
            },
        },
        "required": ["fname", "content"],
    }

    def handle_tool_call(self, input: Dict[str, Any]) -> str | None:
        name = input["fname"]
        content = input["content"]
        file_path = make_file_path(name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as file:
            file.write(content)
        self.track_modified_file(file_path)
        return f"File written successfully: {file_path}"