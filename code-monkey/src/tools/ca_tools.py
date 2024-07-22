import os
import ast
from typing import Dict, List, Any
import json
import networkx as nx
from constants import get_artifacts_dir
from tools.tool import Tool


class ASTParser:
    def __init__(self):
        self.cache: Dict[str, ast.AST] = {}

    def parse_file(self, file_path: str) -> ast.AST:
        if file_path not in self.cache:
            with open(file_path, "r") as file:
                self.cache[file_path] = ast.parse(file.read(), filename=file_path)
        return self.cache[file_path]

    def clear_cache(self):
        self.cache.clear()

    def get_fully_qualified_name(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self.get_fully_qualified_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef):
            return node.name
        else:
            return ""

    def get_imports(self, tree: ast.AST) -> List[Dict[str, Any]]:
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(
                        {"type": "import", "name": alias.name, "alias": alias.asname}
                    )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(
                        {
                            "type": "importfrom",
                            "module": module,
                            "name": f"{module}.{alias.name}" if module else alias.name,
                            "alias": alias.asname,
                        }
                    )
        return imports

    def get_exports(self, tree: ast.AST) -> List[str]:
        exports = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if any(
                    decorator.id == "export"
                    for decorator in node.decorator_list
                    if isinstance(decorator, ast.Name)
                ):
                    exports.append(self.get_fully_qualified_name(node))
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.startswith("__all__"):
                        if isinstance(node.value, ast.List):
                            exports.extend(
                                [
                                    self.get_fully_qualified_name(elt)
                                    for elt in node.value.elts
                                    if isinstance(elt, ast.Str)
                                ]
                            )
        return exports


def resolve_file_path(relative_path: str) -> str:
    return os.path.join(get_artifacts_dir(), relative_path)


def resolve_module_path(module: str) -> str:
    return resolve_file_path(f"{module.replace('.', '/')}.py")


def get_module_name(file_path: str) -> str:
    return os.path.splitext(os.path.relpath(file_path, get_artifacts_dir()))[0].replace(
        "/", "."
    )


class CAASTAnalyzerTool(Tool):
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


class CAImportsTool(Tool):
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


class CAExportsTool(Tool):
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

    def __init__(self, parser: ASTParser):
        self.parser = parser

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


class CADependencyGraphTool(Tool):
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
        self.parser = parser

    def handle_tool_call(self, input: Dict[str, Any]) -> str:
        files = input.get("files", [])
        modules = input.get("modules", [])

        all_files = [resolve_file_path(f) for f in files] + [
            resolve_module_path(m) for m in modules
        ]

        G = nx.DiGraph()

        for file_path in all_files:
            tree = self.parser.parse_file(file_path)
            module_name = get_module_name(file_path)
            G.add_node(module_name)

            for import_info in self.parser.get_imports(tree):
                if import_info["type"] == "import":
                    G.add_edge(module_name, import_info["name"].split(".")[0])
                elif import_info["type"] == "importfrom":
                    G.add_edge(module_name, import_info["module"].split(".")[0])

        dependency_graph = {
            "nodes": list(G.nodes()),
            "edges": list(G.edges()),
            "adjacency_list": nx.to_dict_of_lists(G),
        }
        return json.dumps(dependency_graph, indent=1)
