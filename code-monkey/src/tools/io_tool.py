import os
from typing import Set, Dict, Any
from abc import ABC, abstractmethod
from .tool import Tool
from constants import artifacts_dir


class IOTool(Tool, ABC):
    def __init__(self):
        super().__init__()
        self.modified_files: Set[str] = set()

    def track_modified_file(self, file_path: str):
        self.modified_files.add(os.path.relpath(file_path, artifacts_dir))

    def clear_modified_files(self):
        self.modified_files.clear()

    @abstractmethod
    def handle_tool_call(self, input: Dict[str, Any]) -> str | None:
        pass