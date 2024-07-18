import unittest
from tools.rg_tool import RgTool

class TestRgTool(unittest.TestCase):
    def setUp(self):
        self.rg_tool = RgTool()

    def test_rg_search(self):
        # Test searching for a pattern that should exist
        result = self.rg_tool.handle_tool_call({"pattern": "def handle_tool_call"})
        self.assertIsInstance(result, str)
        self.assertIn("tools/rg_tool.py", result)
        self.assertIn("def handle_tool_call", result)

        # Test searching for a pattern that shouldn't exist
        result = self.rg_tool.handle_tool_call({"pattern": "xJ9qK2pL7mN4rT6vZ"})
        self.assertEqual(result, "0 matches found.")

if __name__ == '__main__':
    unittest.main()