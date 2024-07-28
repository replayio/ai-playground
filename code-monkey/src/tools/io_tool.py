from langchain_core.tools import BaseTool
from langchain_core.callbacks import (
    dispatch_custom_event,
)


class IOTool(BaseTool):
    def notify_file_modified(self, file_path: str):
        dispatch_custom_event("file_modified", file_path)
