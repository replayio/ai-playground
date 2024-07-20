import os
import ast
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum
from collections import defaultdict
from constants import artifacts_dir

class DependencyType(Enum):
    FUNCTION = 1
    CLASS = 2
    VARIABLE = 3


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
        self.full_name: str = f"{module_name}.{name}"
        self.dep_type: DependencyType = dep_type
        self.start_index: int = start_index
        self.end_index: int = end_index

    def __repr__(self):
        return f"Dependency(full_name='{self.full_name}', dep_type={self.dep_type})"

    def __eq__(self, other):
        if not isinstance(other, Dependency):
            return False
        return (self.full_name == other.full_name and
                self.dep_type == other.dep_type)

    def __hash__(self):
        return hash((self.full_name, self.dep_type))

class DependencyImport:
    """
    Represents an import reference to an actual Dependency.
    """

    def __init__(self, module: str, name: str):
        self.module: str = module
        self.name: str = name
        self.module_name: str = module  # Set the module_name attribute

    def __repr__(self):
        return f"DependencyImport(module='{self.module}', name='{self.name}')"


class Module:
    """
    Represents a module with its dependencies and exploration status.
    """

    def __init__(self, name: str):
        self.name: str = name
        self.dependencies: List[Dependency] = []
        self.dependency_imports: List[DependencyImport] = []
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

        content = ""
        line_to_index = {}
        try:
            with open(file_path, "r") as file:
                content = file.read()
                tree = ast.parse(content)
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
        print(f"Analyzing file: {file_path} for module: {module_name}")
        content, tree, line_to_index = self.read_and_parse_file(file_path)
        print(f"File content read and parsed: {file_path}")
        if tree is None:
            print(f"Tree is None for file: {file_path}")
            return

        dependencies = self.find_dependencies(tree, line_to_index)
        print(f"Dependencies found for file {file_path}: {dependencies}")

        for dep in dependencies:
            if isinstance(dep, DependencyImport):
                print(f"Processing import dependency: module_name={dep.module}, name={dep.name}")
                self.add_dependency(
                    module_name,
                    dep.module,
                    None,
                    0,
                    0
                )
                print(f"Added import dependency: module_name={dep.module}, name={dep.name} to module {module_name}")
                self.imported_by[dep.module].add(module_name)
                print(f"Updated imported_by: {self.imported_by}")
                print(f"Current state of modules: {self.modules}")
            else:
                print(f"Processing direct dependency: module_name={module_name}, name={dep.name}, dep_type={dep.dep_type}")
                self.add_dependency(
                    module_name,
                    dep.name,
                    dep.dep_type,
                    dep.start_index,
                    dep.end_index
                )
                print(f"Added direct dependency: module_name={module_name}, name={dep.name}, dep_type={dep.dep_type}")
                print(f"Updated imported_by: {self.imported_by}")
                print(f"Current state of modules: {self.modules}")

        self.modules[module_name].explored = True
        print(f"Module {module_name} marked as explored")
        print(f"Final state of imported_by after analyzing {module_name}: {self.imported_by}")
        print(f"Final state of modules after analyzing {module_name}: {self.modules}")

    def add_module(self, name: str) -> None:
        """
        Add a new module to the graph if it doesn't exist.
        """
        if name not in self.modules:
            self.modules[name] = Module(name)

    def add_dependency(
        self,
        module_name: str,
        name: str,
        dep_type: Optional[DependencyType],
        start_index: int,
        end_index: int,
    ) -> None:
        """
        Add a dependency to a module in the graph.
        """
        self.add_module(module_name)

        if dep_type is not None:
            dependency = Dependency(
                module_name, name, dep_type, start_index, end_index
            )
            # Check if the dependency already exists
            existing_dep = next((dep for dep in self.modules[module_name].dependencies if dep.full_name == dependency.full_name and isinstance(dep, Dependency)), None)
        else:
            dependency = DependencyImport(name, name)
            # Check if the dependency already exists
            existing_dep = next((dep for dep in self.modules[module_name].dependency_imports if dep.module == dependency.module and dep.name == dependency.name and isinstance(dep, DependencyImport)), None)

        if existing_dep:
            # Update the existing dependency if necessary
            if isinstance(existing_dep, Dependency):
                existing_dep.start_index = start_index
                existing_dep.end_index = end_index
        else:
            if isinstance(dependency, Dependency):
                self.modules[module_name].dependencies.append(dependency)
            else:
                self.modules[module_name].dependency_imports.append(dependency)

        # Update lookup tables
        if isinstance(dependency, Dependency):
            self.dep_lookup[dependency.full_name] = dependency
        else:
            self.dep_lookup[f"{dependency.module}.{dependency.name}"] = dependency

        self.modules[module_name].explored = True

        # Ensure uniqueness while preserving order
        self.modules[module_name].dependencies = list({dep.full_name: dep for dep in self.modules[module_name].dependencies}.values())
        self.modules[module_name].dependency_imports = list({f"{dep.module}.{dep.name}": dep for dep in self.modules[module_name].dependency_imports}.values())

    def find_dependencies(
        self,
        tree: ast.AST,
        line_to_index: Dict[int, int]
    ) -> List[Dependency]:
        """
        Extract top-level constructs from a Python AST.
        Returns a list of dependencies.
        """
        dependencies = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start_index = self.get_file_index(node.lineno, node.col_offset, line_to_index)
                end_index = self.get_file_index(node.end_lineno, node.end_col_offset, line_to_index)
                dependencies.append(Dependency("", node.name, DependencyType.FUNCTION, start_index, end_index))
                print(f"Found function dependency: name={node.name}")
            elif isinstance(node, ast.ClassDef):
                start_index = self.get_file_index(node.lineno, node.col_offset, line_to_index)
                end_index = self.get_file_index(node.end_lineno, node.end_col_offset, line_to_index)
                dependencies.append(Dependency("", node.name, DependencyType.CLASS, start_index, end_index))
                print(f"Found class dependency: name={node.name}")
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        start_index = self.get_file_index(node.lineno, node.col_offset, line_to_index)
                        end_index = self.get_file_index(node.end_lineno, node.end_col_offset, line_to_index)
                        dependencies.append(Dependency("", target.id, DependencyType.VARIABLE, start_index, end_index))
                        print(f"Found variable dependency: name={target.id}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.append(DependencyImport(alias.name, alias.asname or alias.name))
                    print(f"Found import dependency: module_name={alias.name}, name={alias.asname or alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module or ""
                for alias in node.names:
                    dependencies.append(DependencyImport(module_name, alias.name))
                    print(f"Found import-from dependency: module_name={module_name}, name={alias.name}")

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
        imported_by = set()
        for dep, importers in self.imported_by.items():
            if dep == module_name or (not dep.startswith('__') and dep.startswith(f"{module_name}.")):
                imported_by.update(importers)
        return imported_by

    def get_dep_imported_by(self, dep_name: str) -> Set[str]:
        """
        Get the set of modules that import the given dependency.
        """
        module_name, name = dep_name.rsplit('.', 1) if '.' in dep_name else ('', dep_name)
        importers = set()
        for importing_module, module in self.modules.items():
            for dep in module.dependencies:
                if dep.name == name and not module_name:
                    importers.add(importing_module)
        return importers


if __name__ == "__main__":
    graph = DependencyGraph()
    graph.analyze_repository(artifacts_dir)
    graph.print_dependencies()
