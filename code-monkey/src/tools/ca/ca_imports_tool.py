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
    files: List[str] | None = Field(
        None, description="List of relative file paths to analyze"
    )
    modules: List[str] | None = Field(None, description="List of modules to analyze")

    # not sure how to encode required rules at all (I think everything defaults to required), and certainly
    # don't know how to encode this one:
    #
    # "anyOf": [{"required": ["files"]}, {"required": ["modules"]}]


class CAImportsTool(CATool):
    """Analyze the imports in Python files"""

    name: str = "ca_analyze_imports"
    description: str = "Analyze the imports in Python files"
    args_schema: Type[BaseModel] = CAImportsToolInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    @instrument("Tool._run", ["files", "modules"], attributes={"tool": "CAImportsTool"})
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

        imports_analysis = {}
        for file_path in all_files:
            tree = self.parser.parse_file(file_path)
            module_name = get_module_name(file_path)
            imports_analysis[module_name] = self.parser.get_imports(tree)

        return json.dumps(imports_analysis, indent=1)
