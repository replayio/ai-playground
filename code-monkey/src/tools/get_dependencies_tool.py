import os
from typing import Type, List, Optional
from pydantic import BaseModel, Field
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from deps import DependencyGraph
from constants import get_artifacts_dir
from instrumentation import instrument


class GetDependenciesToolInput(BaseModel):
    module_names: List[str] = Field(description="List of module names to get dependencies for")


class GetDependenciesTool(BaseTool):
    """Get the dependency graph for one or more Python modules"""
    name: str = "get_dependencies"
    description: str = "Get the dependency graph for one or more Python modules"
    args_schema: Type[BaseModel] = GetDependenciesToolInput

    @instrument("Tool._run", attributes={ "tool": "GetDependenciesTool" })
    def _run(self, module_names: List[str], run_manager: Optional[AsyncCallbackManagerForToolRun])-> str:
        module_names = input["module_names"]
        module_paths = [
            os.path.join(get_artifacts_dir, f"{module}.py") for module in module_names()
        ]
        dependency_graph = DependencyGraph(module_paths)
        dependencies = {
            module.name: [dep.name for dep in module.dependencies]
            for module in dependency_graph.modules.values()
        }
        return str(dependencies)