import os
import ast
from constants import artifacts_dir

class Dependency:
    def __init__(self, name, imports=None, constructs=None):
        self.name = name
        self.imports = imports or []
        self.constructs = constructs or []

class DependencyGraph:
    def __init__(self):
        self.dependencies = {}

    def add_dependency(self, name, imports, constructs):
        self.dependencies[name] = Dependency(name, imports, constructs)

    def get_imports(self, file_path):
        with open(file_path, 'r') as file:
            tree = ast.parse(file.read())
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module if node.module else ''
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        
        return imports

    def get_top_level_constructs(self, file_path):
        with open(file_path, 'r') as file:
            tree = ast.parse(file.read())
        
        constructs = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                constructs.append(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        constructs.append(target.id)
        
        return constructs

    def analyze_repository(self, repo_path):
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    module_name = os.path.splitext(file)[0]
                    imports = self.get_imports(file_path)
                    constructs = self.get_top_level_constructs(file_path)
                    self.add_dependency(module_name, imports, constructs)

    def print_dependencies(self):
        print("\nModule dependencies:")
        for module, dependency in self.dependencies.items():
            print(f"{module}:")
            print("  Imports:")
            for imp in dependency.imports:
                print(f"    -> {imp}")
            print("  Constructs:")
            for construct in dependency.constructs:
                print(f"    - {construct}")
            print()

if __name__ == "__main__":
    graph = DependencyGraph()
    graph.analyze_repository(artifacts_dir)
    graph.print_dependencies()