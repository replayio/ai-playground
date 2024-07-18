import unittest
import os
import tempfile
from deps import DependencyGraph, Dependency

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

        self.assertEqual(len(self.graph.dependencies), 2)
        self.assertIn('file1', self.graph.dependencies)
        self.assertIn('file2', self.graph.dependencies)

        file1_dep = self.graph.dependencies['file1']
        self.assertEqual(file1_dep.imports, ['os'])
        self.assertEqual(file1_dep.constructs, ['func1'])

        file2_dep = self.graph.dependencies['file2']
        self.assertEqual(file2_dep.imports, ['file1.func1'])
        self.assertEqual(file2_dep.constructs, ['MyClass'])

if __name__ == '__main__':
    unittest.main()