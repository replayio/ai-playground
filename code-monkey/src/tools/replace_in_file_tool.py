from typing import Dict, Any
from .io_tool import IOTool
from .utils import make_file_path
from instrumentation import instrument

class ReplaceInFileTool(IOTool):
    name = "replace_in_file"
    description = "Replace a specific string in a file with another string"
    input_schema = {
        "type": "object",
        "properties": {
            "fname": {"type": "string", "description": "Name of the file to edit."},
            "to_replace": {
                "type": "string",
                "description": "The string to be replaced.",
            },
            "replacement": {
                "type": "string",
                "description": "The string to replace with.",
            },
        },
        "required": ["fname", "to_replace", "replacement"],
    }

    @instrument("handle_tool_call", attributes={ "tool": "ReplaceInFileTool" })
    def handle_tool_call(self, input: Dict[str, Any]) -> Dict[str, Any] | None:
        name = input["fname"]
        to_replace = input["to_replace"]
        replacement = input["replacement"]
        file_path = make_file_path(name)
        with open(file_path, "r") as file:
            content = file.read()

        occurrences = content.count(to_replace)
        if occurrences != 1:
            raise Exception(
                f"The string '{to_replace}' appears {occurrences} times in the file. It must appear exactly once for replacement."
            )

        new_content = content.replace(to_replace, replacement)

        with open(file_path, "w") as file:
            file.write(new_content)

        self.track_modified_file(file_path)