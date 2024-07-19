import os
import ast
import sys
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum
from collections import defaultdict
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

    def __init__(
        self,
        module_name: str,
        name: str,
        dep_type: DependencyType,
        start_index: int,
        end_index: int,
    ):
        self.module_name: str = module_name
        self.name: str = name
        self.dep_name: str = f"{module_name}.{name}" if module_name else name
        self.dep_type: DependencyType = dep_type
        self.start_index: int = start_index
        self.end_index: int = end_index

    def __repr__(self):
        return f"Dependency(dep_name='{self.dep_name}', dep_type={self.dep_type})"

    def __eq__(self, other):
        if not isinstance(other, Dependency):
            return False
        return (self.dep_name == other.dep_name and
                self.dep_type == other.dep_type)

    def __hash__(self):
        return hash((self.dep_name, self.dep_type))


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
        self.dep_lookup: Dict[str, Dependency] = {}
        self.file_cache: Dict[str, Tuple[str, ast.AST, Dict[int, int]]] = {}
        self.imported_by: Dict[str, Set[str]] = defaultdict(set)
        if module_paths:
            for path in module_paths:
                module_name = os.path.splitext(os.path.basename(path))[0]
                self.add_module(module_name)
                self.analyze_file(path, module_name)

    def read_and_parse_file(
        self, file_path: str
    ) -> Tuple[str, Optional[ast.AST], Dict[int, int]]:
        """
        Read the file, parse it, and compute line-to-file-index lookup.
        """
        if file_path in self.file_cache:
            return self.file_cache[file_path]

        try:
            with open(file_path, "r") as file:
                content = file.read()
                tree = ast.parse(content)
                line_to_index = {}
                index = 0
                for i, line in enumerate(content.splitlines(keepends=True), 1):
                    line_to_index[i] = index
                    index += len(line)

            self.file_cache[file_path] = (content, tree, line_to_index)
            return content, tree, line_to_index
        except Exception as e:
            print(f"Error parsing file {file_path}: {str(e)}")
            return content, None, line_to_index

    def get_file_index(
        self,
        line: int,
        col: int,
        line_to_index: Dict[int, int]
    ) -> int:
        """
        Convert line and column numbers to file index.
        """
        return line_to_index[line] + col

    def analyze_file(self, file_path: str, module_name: str) -> None:
        """
        Analyze a single file and add its dependencies to the graph.
        """
        content, tree, line_to_index = self.read_and_parse_file(file_path)
        if tree is None:
            return

        dependencies = self.find_dependencies(tree, line_to_index)

        for dep_name in dependencies:
            if dep_name in sys.stdlib_module_names or dep_name == 'sys.path':
                dep_type = DependencyType.IMPORT
            elif '.' in dep_name:
                dep_type = DependencyType.IMPORT
                if dep_name.split('.')[0] not in sys.stdlib_module_names:
                    dep_name = f"{module_name}.{dep_name}"
            elif dep_name.isupper():
                dep_type = DependencyType.VARIABLE
            else:
                dep_type = DependencyType.FUNCTION

            full_dep_name = f"{module_name}.{dep_name}" if module_name and not dep_name.startswith(module_name) else dep_name
            self.add_dependency(
                module_name,
                full_dep_name,
                dep_type,
                0,  # Use 0 as default start_index
                0   # Use 0 as default end_index
            )

        # Ensure that the module's dependencies are correctly updated
        self.modules[module_name].dependencies = list({dep.dep_name: dep for dep in self.modules[module_name].dependencies}.values())

        self.modules[module_name].explored = True

    def add_module(self, name: str) -> None:
        """
        Add a new module to the graph if it doesn't exist.
        """
        if name not in self.modules:
            self.modules[name] = Module(name)

    def add_dependency(
        self,
        module_name: str,
        dep_name: str,
        dep_type: DependencyType,
        start_index: int,
        end_index: int,
    ) -> None:
        """
        Add a dependency to a module in the graph.
        """
        self.add_module(module_name)
        dependency = Dependency(
            module_name, dep_name, dep_type, start_index, end_index
        )

        # Check if the dependency already exists
        existing_dep = next((dep for dep in self.modules[module_name].dependencies if dep.dep_name == dependency.dep_name), None)

        if existing_dep:
            # Update the existing dependency if necessary
            existing_dep.dep_type = dep_type
            existing_dep.start_index = start_index
            existing_dep.end_index = end_index
        else:
            self.modules[module_name].dependencies.append(dependency)

        # Update lookup tables
        self.dep_lookup[dependency.dep_name] = dependency
        self.imported_by[dependency.dep_name].add(module_name)
        self.modules[module_name].explored = True

        # Ensure uniqueness while preserving order
        self.modules[module_name].dependencies = list(dict.fromkeys(self.modules[module_name].dependencies))

    def find_dependencies(
        self,
        tree: ast.AST,
        line_to_index: Dict[int, int]
    ) -> Set[str]:
        """
        Extract imports and top-level constructs from a Python AST.
        Returns a single set of all dependencies.
        """
        dependencies = set()

        def add_dependency(name: str):
            if name not in sys.stdlib_module_names:
                dependencies.add(name)
            else:
                dependencies.add(name.split('.')[-1])

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    add_dependency(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    full_name = f"{module}.{alias.name}" if module else alias.name
                    add_dependency(full_name)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                add_dependency(node.name)
            elif isinstance(node, ast.ClassDef):
                add_dependency(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        # Only add constants (uppercase names) as dependencies
                        if target.id.isupper():
                            add_dependency(target.id)

        # Special handling for 'sys.path'
        if 'sys' in dependencies:
            add_dependency('sys.path')
            dependencies.remove('sys')

        return dependencies

    def analyze_repository(self, repo_path: str) -> Dict[str, List[Dependency]]:
        """
        Analyze the repository and build the dependency graph.
        Returns a dictionary of module names to their dependencies.
        """
        module_dependencies = {}
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    module_name = os.path.splitext(file)[0]

                    self.add_module(module_name)
                    self.analyze_file(file_path, module_name)
                    module_dependencies[module_name] = self.modules[module_name].dependencies

        return module_dependencies

    def get_dep(self, dep_name: str) -> Optional[Dependency]:
        """
        Get a dependency object by its unique name.
        """
        return self.dep_lookup.get(dep_name)

    def print_dependencies(self) -> None:
        """
        Print the dependencies of all modules in the graph.
        """
        print("Module dependencies:")
        for module_name, module in self.modules.items():
            print(f"{module_name} (Explored: {module.explored}):")
            if module.dependencies:
                for dep in module.dependencies:
                    print(
                        f"  -> {dep.name} ({dep.dep_type.name}) "
                        f"[Indexes {dep.start_index}-{dep.end_index}]"
                    )
            else:
                print("  Not analyzed")
            print()

    def get_module_imported_by(self, module_name: str) -> Set[str]:
        """
        Get the set of modules that import the given module or its dependencies.
        """
        return set(
            importer
            for dep, importers in self.imported_by.items()
            if dep == module_name or dep.startswith(f"{module_name}.")
            for importer in importers
        )

    def get_dep_imported_by(self, dep_name: str) -> Set[str]:
        """
        Get the set of modules that import the given dependency.
        """
        return self.imported_by.get(dep_name, set())


if __name__ == "__main__":
    graph = DependencyGraph()
    graph.analyze_repository(artifacts_dir)
    graph.print_dependencies()
