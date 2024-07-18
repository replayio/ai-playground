import unittest
import os
import tempfile
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

    def test_get_imports(self):
        content = """
import os
from sys import path
from module1 import func1, func2
"""
        file_path = self.create_temp_file('test_imports.py', content)
        imports = self.graph.get_imports(file_path)
        self.assertEqual(set(imports), {'os', 'sys.path', 'module1.func1', 'module1.func2'})

    def test_get_top_level_constructs(self):
        content = """
def function1():
    pass

class MyClass:
    def method(self):
        pass

CONSTANT = 42

async def async_function():
    pass
"""
        file_path = self.create_temp_file('test_constructs.py', content)
        constructs = self.graph.get_top_level_constructs(file_path)
        self.assertEqual(set(constructs), {'function1', 'MyClass', 'CONSTANT', 'async_function'})

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

        self.graph.analyze_repository(self.temp_dir)

        self.assertEqual(len(self.graph.modules), 2)
        self.assertIn('file1', self.graph.modules)
        self.assertIn('file2', self.graph.modules)

        file1_module = self.graph.modules['file1']
        self.assertTrue(file1_module.explored)
        file1_imports = [dep.name for dep in file1_module.dependencies if dep.dep_type == DependencyType.IMPORT]
        file1_constructs = [dep.name for dep in file1_module.dependencies if dep.dep_type != DependencyType.IMPORT]
        self.assertEqual(file1_imports, ['os'])
        self.assertEqual(file1_constructs, ['func1'])

        file2_module = self.graph.modules['file2']
        self.assertTrue(file2_module.explored)
        file2_imports = [dep.name for dep in file2_module.dependencies if dep.dep_type == DependencyType.IMPORT]
        file2_constructs = [dep.name for dep in file2_module.dependencies if dep.dep_type != DependencyType.IMPORT]
        self.assertEqual(file2_imports, ['file1.func1'])
        self.assertEqual(file2_constructs, ['MyClass'])

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
        self.graph.analyze_repository(self.temp_dir, partial=True)

        file2_module = self.graph.modules['file2']
        self.assertTrue(file2_module.explored)
        file2_constructs = [dep.name for dep in file2_module.dependencies if dep.dep_type != DependencyType.IMPORT]
        self.assertEqual(set(file2_constructs), {'MyClass', 'new_function'})

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
        self.create_temp_file('file1.py', file1_content)
        self.create_temp_file('file2.py', file2_content)

        self.graph.analyze_repository(self.temp_dir)
        
        partial_graph = DependencyGraph(module_names=['file1'], full_graph=self.graph)
        self.assertEqual(len(partial_graph.modules), 1)
        self.assertIn('file1', partial_graph.modules)
        self.assertNotIn('file2', partial_graph.modules)

if __name__ == '__main__':
    unittest.main()