import unittest
import os
import tempfile
import ast
from deps import DependencyGraph, Dependency, Module, DependencyType

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

        module_dependencies = self.graph.analyze_repository(self.temp_dir)

        self.assertEqual(len(module_dependencies), 2)
        self.assertIn('file1', module_dependencies)
        self.assertIn('file2', module_dependencies)

        file1_deps = module_dependencies['file1']
        file1_imports = [dep for dep in file1_deps if dep.dep_type == DependencyType.IMPORT]
        file1_constructs = [dep for dep in file1_deps if dep.dep_type != DependencyType.IMPORT]

        self.assertTrue(any(dep.dep_name == 'os' and dep.dep_type == DependencyType.IMPORT for dep in file1_deps))
        self.assertTrue(any(dep.dep_name == 'func1' and dep.dep_type != DependencyType.IMPORT for dep in file1_deps))

        file2_deps = module_dependencies['file2']
        file2_imports = [dep for dep in file2_deps if dep.dep_type == DependencyType.IMPORT]
        file2_constructs = [dep for dep in file2_deps if dep.dep_type != DependencyType.IMPORT]

        self.assertTrue(any(dep.dep_name == 'file1.func1' and dep.dep_type == DependencyType.IMPORT for dep in file2_deps))
        self.assertTrue(any(dep.dep_name == 'MyClass' and dep.dep_type != DependencyType.IMPORT for dep in file2_deps))

        # Check imported_by lookup table
        self.assertEqual(self.graph.get_module_imported_by('file1'), {'file2'})
        self.assertEqual(self.graph.get_dep_imported_by('func1'), {'file1'})
        self.assertEqual(self.graph.get_module_imported_by('file2'), set())

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