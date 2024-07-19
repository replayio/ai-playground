import subprocess
import logging
import os
import re
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

    def handle_tool_call(self, input: Dict[str, Any]) -> str:
        pattern = input["pattern"]
        logging.debug(f"artifacts_dir: {artifacts_dir}")

        try:
            return self._search_with_rg(pattern)
        except FileNotFoundError:
            logging.warning("ripgrep (rg) not found. Falling back to Python search.")
            return self._search_with_python(pattern)

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

    def _search_with_python(self, pattern: str) -> str:
        logging.debug(f"Starting Python-based search in current directory: {os.getcwd()}")
        matches = []
        for root, _, files in os.walk('.'):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for i, line in enumerate(f, 1):
                            if re.search(pattern, line, re.IGNORECASE):
                                matches.append(f"{file_path}:{i}:{line.strip()}")
                except Exception as e:
                    logging.error(f"Error reading file {file_path}: {str(e)}")

        if matches:
            return "\n".join(matches)
        else:
            return "0 matches found."