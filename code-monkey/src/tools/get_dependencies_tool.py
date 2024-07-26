import os
from typing import Dict, Any
from .tool import Tool
from deps.deps import DependencyGraph
from constants import get_artifacts_dir
from instrumentation import instrument


class GetDependenciesTool(Tool):
    name = "get_dependencies"
    description = "Get the dependency graph for one or more Python modules"
    input_schema = {
        "type": "object",
        "properties": {
            "module_names": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of module names to get dependencies for",
            },
        },
        "required": ["module_names"],
    }

    @instrument("handle_tool_call", attributes={ "tool": "GetDependenciesTool" })
    def handle_tool_call(self, input: Dict[str, Any]) -> Dict[str, Any] | None:
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