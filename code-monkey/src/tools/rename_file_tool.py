import os
from pydantic import BaseModel, Field
from typing import Type, Optional
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
)
from .io_tool import IOTool
from .utils import make_file_path
from instrumentation import instrument

class RenameFileToolInput(BaseModel):
    old_name: str = Field(description="Current name of the file.")
    new_name: str = Field(description="New name for the file.")

class RenameFileTool(IOTool):
    """Tool to rename a file"""
    name: str = "rename_file"
    description: str = "Rename a file, given old and new names"
    args_schema: Type[BaseModel] = RenameFileToolInput

    @instrument("Tool._run", ["old_name", "new_name"], attributes={ "tool": "RenameFileTool" })
    def _run(self, old_name: str, new_name: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> None:
        old_path = make_file_path(old_name)
        new_path = make_file_path(new_name)

        if not os.path.exists(old_path):
            raise FileNotFoundError(f"The file {old_name} does not exist.")

        new_dir = os.path.dirname(new_path)
        os.makedirs(new_dir, exist_ok=True)

        if os.path.exists(new_path):
            raise FileExistsError(f"The file {new_name} already exists.")

        os.rename(old_path, new_path)
        self.notify_file_modified(old_name)
        self.notify_file_modified(new_name)
        return None
