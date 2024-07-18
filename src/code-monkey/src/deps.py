import os
import ast
from typing import List, Dict, Optional
from enum import Enum
from constants import artifacts_dir

class DependencyType(Enum):
    IMPORT = 1
    FUNCTION = 2
    CLASS = 3
    VARIABLE = 4

class Dependency:
    """
    Represents a top-level symbol dependency.
    """
    def __init__(self, name: str, dep_type: DependencyType):
        self.name: str = name
        self.dep_type: DependencyType = dep_type

class Module:
    """
    Represents a module with its dependencies and exploration status.
    """
    def __init__(self, name: str):
        self.name: str = name
        self.dependencies: List[Dependency] = []
        self.explored: bool = False

class DependencyGraph:
    """
    Represents a graph of dependencies between modules.
    """
    def __init__(self, module_paths: Optional[List[str]] = None):
        self.modules: Dict[str, Module] = {}
        if module_paths:
            for path in module_paths:
                module_name = os.path.splitext(os.path.basename(path))[0]
                self.add_module(module_name)
                self.analyze_file(path, module_name)

    def analyze_file(self, file_path: str, module_name: str) -> None:
        """
        Analyze a single file and add its dependencies to the graph.
        """
        imports = self.get_imports(file_path)
        constructs = self.get_top_level_constructs(file_path)
        
        for imp in imports:
            self.add_dependency(module_name, imp, DependencyType.IMPORT)
        
        for construct in constructs:
            if construct not in imports:
                self.add_dependency(module_name, construct, DependencyType.FUNCTION)  # Assume function for simplicity
        
        self.modules[module_name].explored = True

    def add_module(self, name: str) -> None:
        """
        Add a new module to the graph if it doesn't exist.
        """
        if name not in self.modules:
            self.modules[name] = Module(name)

    def add_dependency(self, module_name: str, dep_name: str, dep_type: DependencyType) -> None:
        """
        Add a dependency to a module in the graph.
        """
        self.add_module(module_name)
        self.modules[module_name].dependencies.append(Dependency(dep_name, dep_type))
        self.modules[module_name].explored = True

    def get_imports(self, file_path: str) -> List[str]:
        """
        Extract imports from a Python file.
        """
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

    def get_top_level_constructs(self, file_path: str) -> List[str]:
        """
        Extract top-level constructs from a Python file.
        """
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

    def analyze_repository(self, repo_path: str, partial: bool = False) -> None:
        """
        Analyze the repository and build the dependency graph.
        If partial is True, only analyze unexplored modules.
        """
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    module_name = os.path.splitext(file)[0]
                    
                    self.add_module(module_name)
                    
                    if not partial or not self.modules[module_name].explored:
                        imports = self.get_imports(file_path)
                        constructs = self.get_top_level_constructs(file_path)
                        
                        for imp in imports:
                            self.add_dependency(module_name, imp, DependencyType.IMPORT)
                        
                        for construct in constructs:
                            if construct in imports:
                                continue
                            self.add_dependency(module_name, construct, DependencyType.FUNCTION)  # Assume function for simplicity

    def print_dependencies(self) -> None:
        """
        Print the dependencies of all modules in the graph.
        """
        print("\nModule dependencies:")
        for module_name, module in self.modules.items():
            print(f"{module_name} (Explored: {module.explored}):")
            if module.dependencies:
                for dep in module.dependencies:
                    print(f"  -> {dep.name} ({dep.dep_type.name})")
            else:
                print("  Not analyzed")
            print()

if __name__ == "__main__":
    graph = DependencyGraph()
    graph.analyze_repository(artifacts_dir)
    graph.print_dependencies()