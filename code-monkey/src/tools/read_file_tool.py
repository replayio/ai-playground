import logging
import traceback
from pydantic import BaseModel, Field
from typing import Type, Optional
from langchain_core.tools import BaseTool
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
)
from .utils import make_file_path
from instrumentation import instrument

class ReadFileToolInput(BaseModel):
    fname: str = Field(description="The filename to read")

class ReadFileTool(BaseTool):
    """Tool that returns the contents of a file given the filename"""
    name: str = "read_file"
    description: str = "Read the contents of the file of given name"
    args_schema: Type[BaseModel] = ReadFileToolInput

    @instrument("Tool._run", ["fname"], attributes={ "tool": "ReadFileTool" })
    def _run(self, fname: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        file_path = make_file_path(fname)
        try:
            with open(file_path, "r") as file:
                content = file.read()
            return content
        except Exception:
           logging.error("Failed to open file for reading: %s", file_path)
           traceback.print_exc()
           # Re-raise the exception
           raise