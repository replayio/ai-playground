import json
from typing import Dict, Any
import networkx as nx
from .ca_tool import CATool
from deps import ASTParser
from deps.deps_utils import resolve_file_path, resolve_module_path, get_module_name

class CADependencyGraphTool(CATool):
    name = "ca_generate_dependency_graph"
    description = "Generate a dependency graph for Python files"
    input_schema = {
        "type": "object",
        "properties": {
            "files": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of relative file paths to analyze",
            },
        },
        "anyOf": [{"required": ["files"]}, {"required": ["modules"]}],
    }

    def __init__(self, parser: ASTParser):
        super().__init__()
        self.parser = parser

    def handle_tool_call(self, input: Dict[str, Any]) -> str:
        files = input.get("files", [])
        modules = input.get("modules", [])

        all_files = [resolve_file_path(f) for f in files] + [
            resolve_module_path(m) for m in modules
        ]

        graph = nx.DiGraph()

        for file_path in all_files:
            tree = self.parser.parse_file(file_path)
            module_name = get_module_name(file_path)
            imports = self.parser.get_imports(tree)

            for imp in imports:
                graph.add_edge(module_name, imp)

        return json.dumps(nx.node_link_data(graph), indent=1)
