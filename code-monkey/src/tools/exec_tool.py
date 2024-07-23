import os
import subprocess
from pydantic import BaseModel, Field
from typing import Type, Optional
from langchain_core.tools import BaseTool
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
)
from .utils import ask_user
from constants import get_artifacts_dir
from code_context import get_all_src_files
from instrumentation import instrument

# Set to store approved commands
approved_commands = set()

class ExecToolInput(BaseModel):
    command: str = Field(description="The command to execute.")
    
class ExecTool(BaseTool):
    """Tool to do some dangerous stuff - execute a command in the terminal"""
    name: str = "exec"
    description: str = "Execute a command in the terminal"
    args_schema: Type[BaseModel] = ExecToolInput

    @instrument("Tool._run", ["command"], attributes={ "tool": "ExecTool" })
    def _run(self, command: str, run_manager: Optional[AsyncCallbackManagerForToolRun])-> str:
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
