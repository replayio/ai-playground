import json
from typing import Dict, Any
from .ca_tool import CATool
from deps.deps_utils import resolve_file_path, resolve_module_path, get_module_name

class CAExportsTool(CATool):
    name = "ca_analyze_exports"
    description = "Analyze the exports in Python files"
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

    def __init__(self):
        super().__init__()

    def handle_tool_call(self, input: Dict[str, Any]) -> str:
        files = input.get("files", [])
        modules = input.get("modules", [])

        all_files = [resolve_file_path(f) for f in files] + [
            resolve_module_path(m) for m in modules
        ]

        exports_analysis = {}
        for file_path in all_files:
            tree = self.parser.parse_file(file_path)
            module_name = get_module_name(file_path)
            exports_analysis[module_name] = self.parser.get_exports(tree)

        return json.dumps(exports_analysis, indent=1)
