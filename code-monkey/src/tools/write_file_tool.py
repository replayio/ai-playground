import os
from pydantic import BaseModel, Field
from typing import Type, Optional
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
)
from .io_tool import IOTool
from .utils import make_file_path
from instrumentation import instrument

class WriteFileToolInput(BaseModel):
    fname: str = Field(description="Name of the file to edit.")
    content: str = Field(description="New contents of the file.")

class WriteFileTool(IOTool):
    """Tool to overwrite a file of given name with passed-in content"""
    name: str = "write_file"
    description: str = "Write content to the file of given name"
    args_schema: Type[BaseModel] = WriteFileToolInput

    @instrument("Tool._run", ["fname", "content"], attributes={ "tool": "WriteFileTool" })
    def _run(self, fname: str, content: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> None:
        file_path = make_file_path(fname)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as file:
            file.write(content)
        self.notify_file_modified(fname)
        return None
