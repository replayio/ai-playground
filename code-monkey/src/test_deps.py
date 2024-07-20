import unittest
import os
import tempfile
import ast
from deps import DependencyGraph, Dependency, DependencyImport, Module, DependencyType

class TestDependencyGraph(unittest.TestCase):
    def setUp(self):
        self.graph = DependencyGraph()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def create_temp_file(self, filename, content):
        file_path = os.path.join(self.temp_dir, filename)
        with open(file_path, 'w') as f:
            f.write(content)
        return file_path

    def test_find_dependencies(self):
        content = """
import os
from sys import path
from module1 import func1, func2

def function1():
    pass

class MyClass:
    def method(self):
        pass

CONSTANT = 42

async def async_function():
    pass
"""
        tree = ast.parse(content)
        deps = self.graph.find_dependencies(tree, {})
        self.assertEqual(deps, {'os', 'sys.path', 'module1.func1', 'module1.func2', 'function1', 'MyClass', 'CONSTANT', 'async_function'})

    def test_analyze_repository(self):
        # Test case 1: Basic import and function definition
        file1_content = """
import os
def func1():
    pass
"""
        file2_content = """
from file1 import func1
import sys as system
class MyClass:
    pass
"""
        self.create_temp_file('file1.py', file1_content)
        self.create_temp_file('file2.py', file2_content)

        # Test case 2: Cyclic import
        file3_content = "from file4 import func4"
        file4_content = "from file3 import *"
        self.create_temp_file('file3.py', file3_content)
        self.create_temp_file('file4.py', file4_content)

        # Test case 3: Empty file
        self.create_temp_file('empty.py', '')

        module_dependencies = self.graph.analyze_repository(self.temp_dir)

        # Check correct number of modules
        self.assertEqual(len(module_dependencies), 5)
        for file in ['file1', 'file2', 'file3', 'file4', 'empty']:
            self.assertIn(file, module_dependencies)

        # Check file1 dependencies
        file1_deps = module_dependencies['file1']
        print(f"Debug: file1_deps = {[f'{type(dep).__name__}({dep.full_name})' for dep in file1_deps]}")
        self.assertTrue(any(isinstance(dep, DependencyImport) and dep.full_name == 'os' for dep in file1_deps))
        self.assertTrue(any(isinstance(dep, Dependency) and dep.full_name == 'file1.func1' for dep in file1_deps))

        # Check os import in file1
        os_dep = next(dep for dep in file1_deps if isinstance(dep, DependencyImport) and dep.full_name == 'os')
        self.assertEqual(os_dep.module, 'os')
        self.assertEqual(os_dep.name, 'os')

        # Check file2 dependencies
        file2_deps = module_dependencies['file2']
        print(f"Debug: file2_deps = {[f'{type(dep).__name__}({dep.full_name})' for dep in file2_deps]}")
        print(f"Debug: Detailed file2_deps = {[(type(dep).__name__, dep.full_name, dep.module if isinstance(dep, DependencyImport) else None, dep.name) for dep in file2_deps]}")
        self.assertTrue(any(isinstance(dep, DependencyImport) and dep.full_name == 'file1.func1' for dep in file2_deps))
        self.assertTrue(any(isinstance(dep, DependencyImport) and dep.full_name == 'sys.system' for dep in file2_deps))

        # Check aliased import in file2
        sys_dep = next(dep for dep in file2_deps if isinstance(dep, DependencyImport) and dep.full_name == 'sys.system')
        self.assertEqual(sys_dep.module, 'sys')
        self.assertEqual(sys_dep.name, 'system')

        self.assertTrue(any(isinstance(dep, Dependency) and dep.full_name == 'file2.MyClass' for dep in file2_deps))

        # Check func1 import in file2
        func1_dep = next(dep for dep in file2_deps if isinstance(dep, DependencyImport) and dep.full_name == 'file1.func1')
        self.assertEqual(func1_dep.module, 'file1')
        self.assertEqual(func1_dep.name, 'func1')

        # Check cyclic import
        file3_deps = module_dependencies['file3']
        file4_deps = module_dependencies['file4']
        self.assertTrue(any(isinstance(dep, DependencyImport) and dep.full_name == 'file4.func4' for dep in file3_deps))
        self.assertTrue(any(isinstance(dep, DependencyImport) and dep.full_name == 'file3.*' for dep in file4_deps))

        # Check empty file
        self.assertEqual(len(module_dependencies['empty']), 0)

        # Check imported_by relationships
        self.assertEqual(self.graph.get_module_imported_by('file1'), {'file2'})
        self.assertEqual(self.graph.get_dep_imported_by('file1.func1'), {'file2'})
        self.assertEqual(self.graph.get_module_imported_by('file2'), set())
        self.assertEqual(self.graph.get_module_imported_by('file3'), {'file4'})
        self.assertEqual(self.graph.get_module_imported_by('file4'), {'file3'})
        self.assertEqual(self.graph.get_module_imported_by('empty'), set())

    def test_partial_analysis(self):
        file1_content = """
import os
def func1():
    pass
"""
        file2_content = """
from file1 import func1
class MyClass:
    pass
"""
        self.create_temp_file('file1.py', file1_content)
        self.create_temp_file('file2.py', file2_content)

        self.graph.analyze_repository(self.temp_dir)

        # Modify file2 and perform partial analysis
        file2_content_modified = """
from file1 import func1
class MyClass:
    pass
def new_function():
    pass
"""
        self.create_temp_file('file2.py', file2_content_modified)
        self.graph.modules['file2'].explored = False
        self.graph.analyze_repository(self.temp_dir)

        file2_module = self.graph.modules['file2']
        self.assertTrue(file2_module.explored)

        with open(os.path.join(self.temp_dir, 'file2.py'), 'r') as file:
            content = file.read()
        tree = ast.parse(content)
        file2_deps = self.graph.find_dependencies(tree, {})

        file2_imports = {dep for dep in file2_deps if dep.startswith('file1.')}
        file2_constructs = file2_deps - file2_imports
        self.assertEqual(file2_imports, {'file1.func1'})
        self.assertEqual(file2_constructs, {'MyClass', 'new_function'})

    def test_get_partial_graph(self):
        file1_content = """
import os
def func1():
    pass
"""
        file2_content = """
from file1 import func1
class MyClass:
    pass
"""
        file1_path = self.create_temp_file('file1.py', file1_content)
        self.create_temp_file('file2.py', file2_content)

        self.graph.analyze_repository(self.temp_dir)

        partial_graph = DependencyGraph([file1_path])
        self.assertEqual(len(partial_graph.modules), 1)
        self.assertIn('file1', partial_graph.modules)
        self.assertNotIn('file2', partial_graph.modules)

    def test_get_module_imported_by(self):
        file1_content = """
import os
def func1():
    pass
"""
        file2_content = """
from file1 import func1
class MyClass:
    pass
"""
        self.create_temp_file('file1.py', file1_content)
        self.create_temp_file('file2.py', file2_content)

        self.graph.analyze_repository(self.temp_dir)

        imported_by = self.graph.get_module_imported_by('file1')
        self.assertSetEqual(imported_by, {'file2'})

    def test_get_dep_imported_by(self):
        file1_content = """
import os
def func1():
    pass
"""
        file2_content = """
from file1 import func1
class MyClass:
    pass
"""
        self.create_temp_file('file1.py', file1_content)
        self.create_temp_file('file2.py', file2_content)

        self.graph.analyze_repository(self.temp_dir)

        imported_by = self.graph.get_dep_imported_by('file1.func1')
        self.assertSetEqual(imported_by, {'file2'})

if __name__ == '__main__':
    unittest.main()