import os
from pydantic import BaseModel, Field
from typing import Type, Optional
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
)
from .io_tool import IOTool
from .utils import make_file_path
from instrumentation import instrument


class DeleteFileToolInput(BaseModel):
    fname: str = Field(description="Name of the file to delete.")


class DeleteFileTool(IOTool):
    """Tool to delete a file by name"""

    name: str = "delete_file"
    description: str = "Delete a file by name"
    args_schema: Type[BaseModel] = DeleteFileToolInput

    @instrument("Tool._run", ["fname"], attributes={"tool": "DeleteFileTool"})
    def _run(
        self, fname: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> None:
        file_path = make_file_path(fname)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {fname} does not exist.")

        os.remove(file_path)
        self.notify_file_modified(fname)
        return None
