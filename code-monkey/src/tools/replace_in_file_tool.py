from pydantic import BaseModel, Field
from typing import Type, Optional
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
)
from .io_tool import IOTool
from .utils import make_file_path
from instrumentation import instrument

class ReplaceInFileToolInput(BaseModel):
    fname: str = Field(description="Name of the file to edit.")
    to_replace: str = Field(description="The string to be replaced.")
    replacement: str = Field(description="The string to replace with.")

class ReplaceInFileTool(IOTool):
    """Replace a specific string in a file with another string"""
    name: str = "replace_in_file"
    description: str = "Replace a specific string in a file with another string"
    args_schema: Type[BaseModel] = ReplaceInFileToolInput

    @instrument("Tool._run", [ "fname", "to_replace", "replacement" ], attributes={ "tool": "ReplaceInFileTool" })
    def _run(self, fname: str, to_replace: str, replacement: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> None:
        file_path = make_file_path(fname)
        with open(file_path, "r") as file:
            content = file.read()

        occurrences = content.count(to_replace)
        if occurrences != 1:
            raise Exception(
                f"The string '{to_replace}' appears {occurrences} times in the file. It must appear exactly once for replacement."
            )

        new_content = content.replace(to_replace, replacement)

        with open(file_path, "w") as file:
            file.write(new_content)

        self.notify_file_modified(fname)
