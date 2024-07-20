import os
import ast
from typing import List, Dict, Optional, Tuple, Set, Union
from enum import Enum
from collections import defaultdict
from ..constants import artifacts_dir

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
        self.full_name: str = f"{module_name}.{name}" if module_name else name
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
        self._full_name: str = self._compute_full_name()

    def _compute_full_name(self) -> str:
        if self.module == self.name:
            return self.module
        elif self.module:
            return f"{self.module}.{self.name}"
        else:
            return self.name

    @property
    def full_name(self):
        return self._full_name

    @property
    def module_name(self):
        return self.module

    def __repr__(self):
        return f"DependencyImport(module='{self.module}', name='{self.name}', full_name='{self.full_name}')"

    def __eq__(self, other):
        if not isinstance(other, DependencyImport):
            return False
        return self.full_name == other.full_name

    def __hash__(self):
        return hash(self.full_name)



class Module:
    """
    Represents a module with its dependencies and exploration status.
    """

    def __init__(self, name: str):
        self.name: str = name
        self.dependencies: List[Dependency] = []
        self.dependency_imports: List[DependencyImport] = []
        self.explored: bool = False

    def __repr__(self):
        return f"Module(name={self.name}, dependencies={self.dependencies}, dependency_imports={self.dependency_imports}, explored={self.explored})"


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
        print(f"\n=== Analyzing file: {file_path} for module: {module_name} ===")
        content, tree, line_to_index = self.read_and_parse_file(file_path)
        if tree is None:
            print(f"Error: AST is None for file: {file_path}")
            return

        dependencies = self.find_dependencies(tree, line_to_index)
        print(f"Dependencies found for {module_name}: {dependencies}")

        for dep in dependencies:
            if isinstance(dep, DependencyImport):
                self.add_dependency(
                    module_name,
                    dep.module,
                    dep.name,
                    0,
                    0,
                    DependencyType.VARIABLE,
                    is_import=True
                )
                print(f"Debug: Added {type(dep).__name__} with full_name: {dep.full_name}")
                print(f"Debug: Added import dependency: {dep.full_name} to module {module_name}")
                print(f"Debug: Updated imported_by[{dep.module}] with {module_name}")
                print(f"Debug: Updated imported_by[{dep.full_name}] with {module_name}")
                self.imported_by[dep.module].add(module_name)
                self.imported_by[dep.full_name].add(module_name)
            elif isinstance(dep, Dependency):
                full_name = f"{module_name}.{dep.name}"
                self.add_dependency(
                    module_name,
                    full_name,
                    dep.name,
                    dep.start_index,
                    dep.end_index,
                    dep.dep_type,
                    is_import=False
                )
                print(f"Debug: Added {type(dep).__name__} with full_name: {full_name}")
                print(f"Debug: Added direct dependency: {full_name} (type: {dep.dep_type}) to module {module_name}")
                print(f"Debug: Updated imported_by[{full_name}] with {module_name}")
                self.imported_by[full_name].add(module_name)

        self.modules[module_name].explored = True
        print(f"\nModule {module_name} marked as explored")
        print(f"Final state of module {module_name}:")
        print(f"  Dependencies: {[dep.full_name for dep in self.modules[module_name].dependencies]}")
        print(f"  Dependency Imports: {[dep.full_name for dep in self.modules[module_name].dependency_imports]}")
        print(f"  Imported by: {self.get_module_imported_by(module_name)}")
        print(f"=== Finished analyzing {module_name} ===\n")



    def add_module(self, name: str) -> None:
        """
        Add a new module to the graph if it doesn't exist.
        """
        if name not in self.modules:
            self.modules[name] = Module(name)

    def add_dependency(
        self,
        module_name: str,
        dep_module: str,
        name: str,
        start_index: int,
        end_index: int,
        dep_type: Optional[DependencyType] = None,
        is_import: bool = False
    ) -> None:
        """
        Add a dependency to a module in the graph.
        """
        self.add_module(module_name)

        print(f"Adding dependency: module={module_name}, dep_module={dep_module}, name={name}, is_import={is_import}")

        if is_import:
            dependency = DependencyImport(dep_module, name)
            full_name = dependency.full_name  # This uses the _compute_full_name method
            existing_dep = next((dep for dep in self.modules[module_name].dependency_imports if dep.full_name == full_name), None)
            if not existing_dep:
                self.modules[module_name].dependency_imports.append(dependency)
                self.dep_lookup[full_name] = dependency
            self.imported_by[dep_module].add(module_name)
            print(f"Added import dependency: {full_name} to module {module_name}")
        else:
            full_name = f"{module_name}.{name}" if module_name else name
            dependency = Dependency(module_name, name, dep_type, start_index, end_index)
            existing_dep = next((dep for dep in self.modules[module_name].dependencies if dep.full_name == full_name), None)
            if existing_dep:
                existing_dep.start_index = start_index
                existing_dep.end_index = end_index
                existing_dep.dep_type = dep_type
            else:
                self.modules[module_name].dependencies.append(dependency)
                self.dep_lookup[full_name] = dependency
            self.imported_by[dep_module].add(module_name)
            print(f"Added direct dependency: {full_name} (type: {dep_type}) to module {module_name}")

        self.modules[module_name].explored = True

        # Ensure uniqueness while preserving order
        self.modules[module_name].dependencies = list({dep.full_name: dep for dep in self.modules[module_name].dependencies}.values())
        self.modules[module_name].dependency_imports = list({dep.full_name: dep for dep in self.modules[module_name].dependency_imports}.values())

        print(f"Module {module_name} after adding dependency:")
        print(f"  Dependencies: {[dep.full_name for dep in self.modules[module_name].dependencies]}")
        print(f"  Dependency Imports: {[dep.full_name for dep in self.modules[module_name].dependency_imports]}")

    def find_dependencies(
        self,
        tree: ast.AST,
        line_to_index: Dict[int, int]
    ) -> List[Union[Dependency, DependencyImport]]:
        """
        Extract top-level constructs from a Python AST.
        Returns a list of dependencies and dependency imports.
        """
        dependencies = []

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start_index = self.get_file_index(node.lineno, node.col_offset, line_to_index)
                end_index = self.get_file_index(node.end_lineno, node.end_col_offset, line_to_index)
                dependencies.append(Dependency("", node.name, DependencyType.FUNCTION, start_index, end_index))
            elif isinstance(node, ast.ClassDef):
                start_index = self.get_file_index(node.lineno, node.col_offset, line_to_index)
                end_index = self.get_file_index(node.end_lineno, node.end_col_offset, line_to_index)
                dependencies.append(Dependency("", node.name, DependencyType.CLASS, start_index, end_index))
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        start_index = self.get_file_index(node.lineno, node.col_offset, line_to_index)
                        end_index = self.get_file_index(node.end_lineno, node.end_col_offset, line_to_index)
                        dependencies.append(Dependency("", target.id, DependencyType.VARIABLE, start_index, end_index))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.append(DependencyImport(alias.name, alias.asname or alias.name))
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module or ""
                for alias in node.names:
                    dependencies.append(DependencyImport(module_name, alias.name))

        return dependencies

    def analyze_repository(self, repo_path: str) -> Dict[str, List[Union[Dependency, DependencyImport]]]:
        """
        Analyze the repository and build the dependency graph.
        Returns a dictionary of module names to their dependencies and dependency imports.
        """
        print("Debug: Starting analyze_repository")
        module_dependencies = {}
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    module_name = os.path.splitext(file)[0]

                    print(f"Debug: Analyzing file: {file_path}")
                    self.add_module(module_name)
                    self.analyze_file(file_path, module_name)
                    module_dependencies[module_name] = (
                        self.modules[module_name].dependencies +
                        self.modules[module_name].dependency_imports
                    )
                    print(f"Debug: Module {module_name} dependencies:")
                    for dep in module_dependencies[module_name]:
                        print(f"  - {dep.__class__.__name__}: {dep.full_name}")

        print(f"Debug: Final module_dependencies before return:")
        for module, deps in module_dependencies.items():
            print(f"  {module}:")
            for dep in deps:
                print(f"    - {dep.__class__.__name__}: {dep.full_name}")
                if isinstance(dep, DependencyImport):
                    print(f"      Module: {dep.module}, Name: {dep.name}")
        return module_dependencies

    def get_dep(self, dep_name: str) -> Optional[Union[Dependency, DependencyImport]]:
        """
        Get a dependency object by its unique name.
        """
        return self.dep_lookup.get(dep_name)

    def get_all_dependencies(self, module_name: str) -> List[Union[Dependency, DependencyImport]]:
        """
        Get all dependencies (both Dependency and DependencyImport) for a given module.
        """
        if module_name not in self.modules:
            return []
        return self.modules[module_name].dependencies + self.modules[module_name].dependency_imports

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
        # Remove the module itself from the set of importers
        imported_by.discard(module_name)
        return imported_by

    def get_dep_imported_by(self, dep_name: str) -> Set[str]:
        """
        Get the set of modules that import the given dependency.
        """
        print(f"Debug: get_dep_imported_by called with dep_name: {dep_name}")
        importers = self.imported_by.get(dep_name, set())

        # Handle the case where dep_name is a full name (e.g., 'file1.func1')
        if '.' in dep_name:
            module_name, _ = dep_name.split('.', 1)
            importers.update(self.imported_by.get(module_name, set()))
            # Remove the defining module from the set of importers
            importers.discard(module_name)

        print(f"Debug: Importers for {dep_name}: {importers}")
        return importers


if __name__ == "__main__":
    graph = DependencyGraph()
    graph.analyze_repository(artifacts_dir)
    graph.print_dependencies()
