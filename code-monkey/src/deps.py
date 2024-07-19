import os
import ast
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
        self.dep_name: str = f"{module_name}.{name}"
        self.name: str = name
        self.dep_type: DependencyType = dep_type
        self.start_index: int = start_index
        self.end_index: int = end_index


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
    ) -> Tuple[str, ast.AST, Dict[int, int]]:
        """
        Read the file, parse it, and compute line-to-file-index lookup.
        """
        if file_path in self.file_cache:
            return self.file_cache[file_path]

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
        dependencies = self.find_dependencies(tree, line_to_index)

        for dep in dependencies:
            self.add_dependency(
                module_name,
                dep.name,
                dep.dep_type,
                dep.start_index,
                dep.end_index
            )

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
        self.modules[module_name].dependencies.append(dependency)
        self.dep_lookup[dependency.dep_name] = dependency
        self.imported_by[dep_name].add(module_name)
        self.modules[module_name].explored = True

    def find_dependencies(
        self,
        tree: ast.AST,
        line_to_index: Dict[int, int]
    ) -> List[Dependency]:
        """
        Extract imports and top-level constructs from a Python AST.
        """
        dependencies = []

        # Extract imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    start = self.get_file_index(
                        node.lineno, node.col_offset, line_to_index
                    )
                    end = self.get_file_index(
                        node.end_lineno, node.end_col_offset, line_to_index
                    )
                    dependencies.append(
                        Dependency(
                            "", alias.name, DependencyType.IMPORT, start, end
                        )
                    )
            elif isinstance(node, ast.ImportFrom):
                module = node.module if node.module else ""
                for alias in node.names:
                    start = self.get_file_index(
                        node.lineno, node.col_offset, line_to_index
                    )
                    end = self.get_file_index(
                        node.end_lineno, node.end_col_offset, line_to_index
                    )
                    dependencies.append(
                        Dependency(
                            "",
                            f"{module}.{alias.name}",
                            DependencyType.IMPORT,
                            start,
                            end
                        )
                    )

        # Extract top-level constructs
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef,
                                 ast.AsyncFunctionDef)):
                start = self.get_file_index(
                    node.lineno, node.col_offset, line_to_index
                )
                end = self.get_file_index(
                    node.end_lineno, node.end_col_offset, line_to_index
                )
                dep_type = (
                    DependencyType.CLASS
                    if isinstance(node, ast.ClassDef)
                    else DependencyType.FUNCTION
                )
                dependencies.append(
                    Dependency("", node.name, dep_type, start, end)
                )
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        start = self.get_file_index(
                            node.lineno, node.col_offset, line_to_index
                        )
                        end = self.get_file_index(
                            node.end_lineno, node.end_col_offset, line_to_index
                        )
                        dependencies.append(
                            Dependency(
                                "", target.id, DependencyType.VARIABLE,
                                start, end
                            )
                        )

        return dependencies

    def analyze_repository(self, repo_path: str) -> None:
        """
        Analyze the repository and build the dependency graph.
        """
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    module_name = os.path.splitext(file)[0]

                    self.add_module(module_name)
                    self.analyze_file(file_path, module_name)

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
        Get the set of modules that import the given module.
        """
        return {
            importer
            for dep, importers in self.imported_by.items()
            if dep.startswith(f"{module_name}.")
            for importer in importers
        }

    def get_dep_imported_by(self, dep_name: str) -> Set[str]:
        """
        Get the set of modules that import the given dependency.
        """
        return self.imported_by.get(dep_name, set())


if __name__ == "__main__":
    graph = DependencyGraph()
    graph.analyze_repository(artifacts_dir)
    graph.print_dependencies()
