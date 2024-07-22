import os
from typing import Dict, Any
from .tool import Tool
from deps.deps import DependencyGraph
from constants import artifacts_dir


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

    def handle_tool_call(self, input: Dict[str, Any]) -> Dict[str, Any] | None:
        module_names = input["module_names"]
        module_paths = [
            os.path.join(artifacts_dir, f"{module}.py") for module in module_names
        ]
        dependency_graph = DependencyGraph(module_paths)
        dependencies = {
            module.name: [dep.name for dep in module.dependencies]
            for module in dependency_graph.modules.values()
        }
        return str(dependencies)