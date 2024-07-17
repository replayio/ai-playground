import os
import shutil
import tempfile
import unittest
from tools import copy_src, artifacts_dir, src_dir


class TestCopySrc(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.original_artifacts_dir = artifacts_dir
        self.original_src_dir = src_dir

        # Override artifacts_dir and src_dir for testing
        global artifacts_dir, src_dir
        artifacts_dir = os.path.join(self.temp_dir, "artifacts")
        src_dir = os.path.join(self.temp_dir, "src")

        # Create a mock source directory structure
        os.makedirs(src_dir)
        os.makedirs(os.path.join(src_dir, "subdir"))
        with open(os.path.join(src_dir, "file1.txt"), "w") as f:
            f.write("test1")
        with open(os.path.join(src_dir, "subdir", "file2.txt"), "w") as f:
            f.write("test2")

    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.temp_dir)

        # Restore original artifacts_dir and src_dir
        global artifacts_dir, src_dir
        artifacts_dir = self.original_artifacts_dir
        src_dir = self.original_src_dir

    def test_copy_src(self):
        result = copy_src()

        # Check if all files are copied and listed correctly
        expected_files = ["file1.txt", os.path.join("subdir", "file2.txt")]
        self.assertEqual(sorted(result), sorted(expected_files))

        # Check if files are actually copied to the artifacts directory
        for file in expected_files:
            self.assertTrue(os.path.exists(os.path.join(artifacts_dir, file)))

        # Check file contents
        with open(os.path.join(artifacts_dir, "file1.txt"), "r") as f:
            self.assertEqual(f.read(), "test1")
        with open(os.path.join(artifacts_dir, "subdir", "file2.txt"), "r") as f:
            self.assertEqual(f.read(), "test2")


if __name__ == "__main__":
    unittest.main()
