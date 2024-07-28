import subprocess
import logging
import os
from typing import Type, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
)
from constants import get_artifacts_dir
from instrumentation import instrument


class RgToolInput(BaseModel):
    pattern: str = Field(description="The pattern to search for.")


class RgTool(BaseTool):
    """Search for a pattern in files within the artifacts folder using ripgrep"""

    name: str = "rg"
    description: str = (
        "Search for a pattern in files within the artifacts folder using ripgrep"
    )
    args_schema: Type[BaseModel] = RgToolInput

    @instrument("Tool._run", ["pattern"], attributes={"tool": "RgTool"})
    def _run(
        self, pattern: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        logging.debug(f"get_artifacts_dir(): {get_artifacts_dir()}")

        return self._search_with_rg(pattern)

    def _search_with_rg(self, pattern: str) -> str:
        command = ["rg", "-i", "--no-heading", "--with-filename", "-r", pattern, "."]
        logging.debug(f"Current working directory: {os.getcwd()}")
        logging.debug(f"Executing command: {' '.join(command)}")

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
            )

            logging.debug(f"Raw output: {result.stdout}")

            if result.stdout.strip():
                return result.stdout.strip()
            else:
                return "0 matches found."
        except subprocess.CalledProcessError as e:
            if e.returncode == 1:  # No matches
                logging.debug("No matches found")
                return "0 matches found."
            else:
                logging.error(f"Error occurred: {e.stderr}")
                raise Exception(f"Error occurred: {e.stderr}")
