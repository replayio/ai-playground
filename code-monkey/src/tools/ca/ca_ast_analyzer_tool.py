import json
from typing import Dict, Any
from .ca_tool import CATool
from deps import ASTParser
from deps.deps_utils import resolve_file_path, resolve_module_path

class CAASTAnalyzerTool(CATool):
    name = "ca_analyze_ast"
    description = "Analyze the Abstract Syntax Tree of Python files"
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

        summaries = self.parser.summarize_modules(all_files)

        return json.dumps(summaries, indent=1)
