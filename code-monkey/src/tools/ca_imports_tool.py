import json
from typing import Dict, Any
from .ca_tool_base import CATool
from .ast_parser import ASTParser
from .utils import resolve_file_path, resolve_module_path, get_module_name

class CAImportsTool(CATool):
    name = "ca_analyze_imports"
    description = "Analyze the imports in Python files"
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

        imports_analysis = {}
        for file_path in all_files:
            tree = self.parser.parse_file(file_path)
            module_name = get_module_name(file_path)
            imports_analysis[module_name] = self.parser.get_imports(tree)

        return json.dumps(imports_analysis, indent=1)
