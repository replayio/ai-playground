import json
from pydantic import BaseModel, Field
from typing import Type, List, Optional, Any
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
)
import networkx as nx
from .ca_tool import CATool
from deps import resolve_file_path, resolve_module_path, get_module_name
from instrumentation import instrument


class CADependencyGraphToolInput(BaseModel):
    files: List[str] = Field(None, description="List of relative file paths to analyze")
    modules: List[str] = Field(None, description="List of modules to analyze")

    # not sure how to encode required rules at all (I think everything defaults to required), and certainly
    # don't know how to encode this one:
    #
    # "anyOf": [{"required": ["files"]}, {"required": ["modules"]}]


class CADependencyGraphTool(CATool):
    """Generate a dependency graph for Python files"""

    name = "ca_generate_dependency_graph"
    description = "Generate a dependency graph for Python files"
    args_schema: Type[BaseModel] = CADependencyGraphToolInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    @instrument(
        "Tool._run", ["files", "modules"], attributes={"tool": "CADependencyGraphTool"}
    )
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

        graph = nx.DiGraph()

        for file_path in all_files:
            module_name = get_module_name(file_path)
            imports = self.parser.get_imports(file_path)

            for imp in imports:
                graph.add_edge(module_name, imp)

        return json.dumps(nx.node_link_data(graph), indent=1)
