import ast
from typing import Dict, List


class ModuleSummary:
    functions: List[str]
    classes: List[str]
    imports: List[str]
    exports: List[str]


class ASTParser:
    cache: Dict[str, ast.AST]

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

    def get_imports(self, file_path: str) -> List[str]:
        imports = []
        for node in ast.walk(self.cache[file_path]):
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

    def get_exports(self, file_path: str) -> List[str]:
        exports = []
        for node in ast.walk(self.cache[file_path]):
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

    def summarize_modules(self, files: List[str]) -> Dict[str, ModuleSummary]:
        summaries = {}
        for file_path in files:
            self.parse_file(file_path)  # Ensure the file is parsed
            summary = ModuleSummary()
            summary.functions = [
                self.get_fully_qualified_name(node)
                for node in ast.walk(self.cache[file_path])
                if isinstance(node, ast.FunctionDef)
            ]
            summary.classes = [
                self.get_fully_qualified_name(node)
                for node in ast.walk(self.cache[file_path])
                if isinstance(node, ast.ClassDef)
            ]
            summary.imports = self.get_imports(file_path)
            summary.exports = self.get_exports(file_path)
            summaries[file_path] = summary

        return summaries
