import os
from typing import Dict, Any
from .io_tool import IOTool
from .utils import make_file_path

class CreateFileTool(IOTool):
    name = "create_file"
    description = "Create a new file with optional content"
    input_schema = {
        "type": "object",
        "properties": {
            "fname": {
                "type": "string",
                "description": "Name of the file to create.",
            },
            "content": {
                "type": "string",
                "description": "Initial content of the file (optional).",
            },
        },
        "required": ["fname"],
    }

    def handle_tool_call(self, input: Dict[str, Any]) -> Dict[str, Any] | None:
        name = input["fname"]
        content = input.get("content", "")
        file_path = make_file_path(name)

        if os.path.exists(file_path):
            raise FileExistsError(f"The file {name} already exists.")

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as file:
            file.write(content)

        self.track_modified_file(file_path)