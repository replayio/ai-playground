import unittest
from tools import RgTool
import re

class TestRgTool(unittest.TestCase):
    def setUp(self):
        self.rg_tool = RgTool()

    def test_rg_search(self):
        # Test searching for a pattern that should exist
        result = self.rg_tool._run("class RgTool")

        # Assert that the result is a non-empty string
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, "", "Search result should not be empty")

        # Assert that the result contains at least one valid file path
        self.assertRegex(result, r'^[^\n]+:', "Result should contain at least one valid file path")

        # Assert that the result contains at least one occurrence of "class RgTool"
        self.assertIn("class RgTool", result, "Result should contain at least one occurrence of 'class RgTool'")

        # Assert that the result contains data from at least one file
        files = set(re.findall(r'^(.+?):', result, re.MULTILINE))
        self.assertGreaterEqual(len(files), 1, "Result should contain data from at least one file")

        # Ensure the result doesn't contain any unexpected content
        self.assertNotRegex(result, r"error|exception|traceback", re.IGNORECASE)

if __name__ == '__main__':
    unittest.main()
