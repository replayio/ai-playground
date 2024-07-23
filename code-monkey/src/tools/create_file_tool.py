import os
from pydantic import BaseModel, Field
from typing import Type, Optional
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
)
from .io_tool import IOTool
from .utils import make_file_path
from instrumentation import instrument

class CreateFileToolInput(BaseModel):
    fname: str = Field(description="Name of the file to create.")
    content: Optional[str] = Field(description="Initial content of the file (optional).")

class CreateFileTool(IOTool):
    """Tool to create a new file with optional content"""
    name: str = "create_file"
    description: str = "Create a new file with optional content"
    args_schema: Type[BaseModel] = CreateFileToolInput

    @instrument("Tool._run", ["fname", "content"], attributes={ "tool": "CreateFileTool" })
    def _run(self, fname: str, content: str | None = None, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> None:
        file_path = make_file_path(fname)

        if os.path.exists(file_path):
            raise FileExistsError(f"The file {fname} already exists.")

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as file:
            file.write(content)

        self.notify_file_modified(fname)
