import json
from pydantic import BaseModel, Field
from typing import Type, List, Optional, Any
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
)
from .ca_tool import CATool
from deps import resolve_file_path, resolve_module_path, get_module_name
from instrumentation import instrument


class CAImportsToolInput(BaseModel):
    files: List[str] = Field(None, description="List of relative file paths to analyze")
    modules: List[str] = Field(None, description="List of modules to analyze")

    # not sure how to encode required rules at all (I think everything defaults to required), and certainly
    # don't know how to encode this one:
    #
    # "anyOf": [{"required": ["files"]}, {"required": ["modules"]}]


class CAExportsTool(CATool):
    """Analyze the exports in Python files"""

    name = "ca_analyze_exports"
    description = "Analyze the exports in Python files"
    args_schema: Type[BaseModel] = CAImportsToolInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    @instrument("Tool._run", ["files", "modules"], attributes={"tool": "CAExportsTool"})
    def _run(
        self,
        files: List[str] | None,
        modules: List[str] | None,
        run_manager: Optional[AsyncCallbackManagerForToolRun],
    ) -> str:
        if files is None:
            files = []
        if modules is None:
            modules = []

        all_files = [resolve_file_path(f) for f in files] + [
            resolve_module_path(m) for m in modules
        ]

        exports_analysis = {}
        for file_path in all_files:
            module_name = get_module_name(file_path)
            exports_analysis[module_name] = self.parser.get_exports(file_path)

        return json.dumps(exports_analysis, indent=1)
