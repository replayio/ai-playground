import subprocess
from typing import Dict, Any
from .tool import Tool
from constants import artifacts_dir


class RgTool(Tool):
    name = "rg"
    description = (
        "Search for a pattern in files within the artifacts folder using ripgrep"
    )
    input_schema = {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "The pattern to search for.",
            },
        },
        "required": ["pattern"],
    }

    def handle_tool_call(self, input: Dict[str, Any]) -> Dict[str, Any] | None:
        pattern = input["pattern"]
        try:
            result = subprocess.run(
                ["rg", "-i", pattern, artifacts_dir],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            if e.returncode == 1:  # No matches
                return "0 matches found."
            else:
                raise Exception(f"Error occurred: {e.stderr}")