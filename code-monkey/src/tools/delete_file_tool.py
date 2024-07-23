import os
from typing import Dict, Any
from .io_tool import IOTool
from .utils import make_file_path
from instrumentation import instrument

class DeleteFileTool(IOTool):
    name = "delete_file"
    description = "Delete a file"
    input_schema = {
        "type": "object",
        "properties": {
            "fname": {
                "type": "string",
                "description": "Name of the file to delete.",
            },
        },
        "required": ["fname"],
    }

    @instrument("handle_tool_call", attributes={ "tool": "DeleteFileTool" })
    def handle_tool_call(self, input: Dict[str, Any]) -> Dict[str, Any] | None:
        name = input["fname"]
        file_path = make_file_path(name)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {name} does not exist.")

        os.remove(file_path)
        self.track_modified_file(file_path)