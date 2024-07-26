import os
import subprocess
from typing import Dict, Any
from .tool import Tool
from .utils import ask_user
from constants import get_artifacts_dir
from code_context import get_all_src_files
from instrumentation import instrument

# Set to store approved commands
approved_commands = set()

class ExecTool(Tool):
    name = "exec"
    description = "Execute a command in the terminal"
    input_schema = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "The command to execute."},
        },
        "required": ["command"],
    }

    @instrument("handle_tool_call", attributes={ "tool": "ExecTool" })
    def handle_tool_call(self, input: Dict[str, Any]) -> Dict[str, Any] | None:
        command = input["command"]
        # TODO: fix this based on copy_src
        file_tree = get_all_src_files()

        # Convert matching file names to absolute paths
        command_parts = command.split()
        for i, part in enumerate(command_parts):
            if part in file_tree:
                command_parts[i] = os.path.join(get_artifacts_dir(), part)

        modified_command = " ".join(command_parts)

        if modified_command not in approved_commands:
            confirmation = ask_user(
                f"Do you want to execute the following command? [Y/n]\n{modified_command}"
            )
            if confirmation.lower() != "y" and confirmation != "":
                raise Exception("Command execution cancelled by user.")
            approved_commands.add(modified_command)

        try:
            result = subprocess.run(
                modified_command, shell=True, capture_output=True, text=True, check=True
            )
            return f"stdout={result.stdout}\nstderr={result.stderr}"
        except subprocess.CalledProcessError as e:
            error_message = (
                f"Command execution failed with return code {e.returncode}.\n"
            )
            error_message += f"Command: {modified_command}\n"
            error_message += f"Stdout: {e.stdout}\n"
            error_message += f"Stderr: {e.stderr}"
            raise Exception(error_message)
