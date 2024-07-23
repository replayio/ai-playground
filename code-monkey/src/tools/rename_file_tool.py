import os
from typing import Dict, Any
from .io_tool import IOTool
from .utils import make_file_path
from instrumentation import instrument

class RenameFileTool(IOTool):
    name = "rename_file"
    description = "Rename a file"
    input_schema = {
        "type": "object",
        "properties": {
            "old_name": {
                "type": "string",
                "description": "Current name of the file.",
            },
            "new_name": {"type": "string", "description": "New name for the file."},
        },
        "required": ["old_name", "new_name"],
    }

    @instrument("handle_tool_call", attributes={ "tool": "RenameFileTool" })
    def handle_tool_call(self, input: Dict[str, Any]) -> Dict[str, Any] | None:
        old_name = input["old_name"]
        new_name = input["new_name"]
        old_path = make_file_path(old_name)
        new_path = make_file_path(new_name)

        if not os.path.exists(old_path):
            raise FileNotFoundError(f"The file {old_name} does not exist.")

        new_dir = os.path.dirname(new_path)
        os.makedirs(new_dir, exist_ok=True)

        if os.path.exists(new_path):
            raise FileExistsError(f"The file {new_name} already exists.")

        os.rename(old_path, new_path)
        self.track_modified_file(old_path)
        self.track_modified_file(new_path)