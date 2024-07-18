import os
import subprocess
from typing import Dict, Any
from .tool import Tool
from .utils import make_file_path

class RunTestTool(Tool):
    name = "run_test"
    description = "Run Python tests in a given file and return the results"
    input_schema = {
        "type": "object",
        "properties": {
            "fname": {
                "type": "string",
                "description": "Name of the test file to run.",
            },
        },
        "required": ["fname"],
    }

    def handle_tool_call(self, input: Dict[str, Any]) -> Dict[str, Any] | None:
        name = input["fname"]
        file_path = make_file_path(name)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {name} does not exist.")

        result = subprocess.run(
            ["python", "-m", "unittest", file_path],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(file_path),
        )
        return f"returncode={str(result.returncode)}\nstdout={result.stdout}\nstderr={result.stderr}"