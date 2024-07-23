import unittest
import sys
import os
import shutil
sys.path.append('..')
from deps.ASTParser import ASTParser

class TestASTParser(unittest.TestCase):
    def setUp(self):
        self.parser = ASTParser()
        self.mock_files_dir = 'mock_files'
        self.test_file1 = os.path.join(self.mock_files_dir, 'test_file1.py')
        self.test_file2 = os.path.join(self.mock_files_dir, 'test_file2.py')

        # Ensure the mock_files directory exists
        os.makedirs(self.mock_files_dir, exist_ok=True)

        # Generate mock test files
        with open(self.test_file1, 'w') as f:
            f.write("import os\nfrom test_file2 import sample_function\n\ndef main():\n    pass")

        with open(self.test_file2, 'w') as f:
            f.write("def sample_function():\n    pass")

        # Pre-populate the cache with ASTs for the test files
        self.parser.parse_file(self.test_file1)
        self.parser.parse_file(self.test_file2)

    def tearDown(self):
        # Clean up generated files after tests
        shutil.rmtree(self.mock_files_dir)

    def test_parse_file(self):
        # Test that parse_file returns an AST for a valid file path
        ast = self.parser.parse_file(self.test_file1)
        self.assertIsNotNone(ast)
        # Test that the AST is stored in the cache
        self.assertIn(self.test_file1, self.parser.cache)

    def test_get_imports(self):
        # Test that get_imports returns a list of imports for a given file path
        imports = self.parser.get_imports(self.test_file1)
        self.assertIsInstance(imports, list)
        # Test that the list of imports is correct
        self.assertEqual(set(imports), {'os', 'test_file2.sample_function'})

    def test_get_exports(self):
        # Test that get_exports returns a list of exports for a given file path
        exports = self.parser.get_exports(self.test_file1)
        self.assertIsInstance(exports, list)
        # Test that the list of exports is correct
        # This is a placeholder; actual implementation will depend on the file structure and contents

    def test_summarize_modules(self):
        # Test that summarize_modules returns a summary for a list of file paths
        summary = self.parser.summarize_modules([self.test_file1, self.test_file2])
        self.assertIsInstance(summary, dict)
        # Test that the summary is correct for each file
        # This is a placeholder; actual implementation will depend on the file structure and contents

if __name__ == '__main__':
    unittest.main()
