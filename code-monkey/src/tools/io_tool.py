from langchain_core.tools import BaseTool
from langchain_core.callbacks import (
    dispatch_custom_event,
)
from constants import get_artifacts_dir

class IOTool(BaseTool):
    def notify_file_modified(self, file_path: str):
        dispatch_custom_event("file_modified", os.path.relpath(file_path, get_artifacts_dir()))
