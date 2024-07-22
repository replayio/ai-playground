import os
import shutil
from typing import List
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern
from constants import artifacts_dir, src_dir
from tools.utils import get_file_tree

class CodeContext:
    def __init__(self):
        self.known_files = []

    def copy_src(self) -> List[str]:
        dest_dir = artifacts_dir

        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        # Read .gitignore patterns
        gitignore_patterns = []
        for i in range(4):  # Check current directory and up to 3 parent directories
            gitignore_path = os.path.join(
                os.path.dirname(__file__), *[".." for _ in range(i)], ".gitignore"
            )
            if os.path.exists(gitignore_path):
                with open(gitignore_path, 'r') as gitignore_file:
                    gitignore_patterns.extend(gitignore_file.read().splitlines())

        # Create PathSpec object
        ignore_spec = PathSpec.from_lines(GitWildMatchPattern, gitignore_patterns)

        for root, dirs, files in os.walk(src_dir):
            for file in files:
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, src_dir)
                if not ignore_spec.match_file(rel_path):
                    dest_path = os.path.join(dest_dir, rel_path)
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(src_path, dest_path)
                    self.known_files.append(rel_path)

        return list(get_file_tree(dest_dir, ignore_spec))