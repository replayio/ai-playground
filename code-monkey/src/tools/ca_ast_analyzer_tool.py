import ast
import json
from typing import Dict, Any
from .ca_tool_base import CATool
from .ast_parser import ASTParser
from .utils import resolve_file_path, resolve_module_path, get_module_name

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

        analysis = {}
        for file_path in all_files:
            tree = self.parser.parse_file(file_path)
            module_name = get_module_name(file_path)

            analysis[module_name] = {
                "functions": [
                    self.parser.get_fully_qualified_name(node)
                    for node in ast.walk(tree)
                    if isinstance(node, ast.FunctionDef)
                ],
                "classes": [
                    self.parser.get_fully_qualified_name(node)
                    for node in ast.walk(tree)
                    if isinstance(node, ast.ClassDef)
                ],
                "imports": self.parser.get_imports(tree),
                "exports": self.parser.get_exports(tree),
            }

        return json.dumps(analysis, indent=1)
