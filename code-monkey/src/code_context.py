import os
import shutil
from typing import List
import pathspec
from constants import artifacts_dir, src_root_dir

def get_all_src_files() -> List[str]:
    files_to_copy = []

    # Read .gitignore patterns
    gitignore_patterns = [".git"]
    for i in range(4):  # Check current directory and up to 3 parent directories
        gitignore_path = os.path.join(
            os.path.dirname(__file__), *[".." for _ in range(i)], ".gitignore"
        )
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r') as gitignore_file:
                gitignore_patterns.extend(gitignore_file.read().splitlines())

    # Create PathSpec object
    ignore_spec = pathspec.GitIgnoreSpec.from_lines(gitignore_patterns)

    for root, dirs, files in os.walk(src_root_dir):
        for file in files:
            src_path = os.path.join(root, file)
            rel_path = os.path.relpath(src_path, src_root_dir)
            if not ignore_spec.match_file(rel_path):
                files_to_copy.append(rel_path)
    return files_to_copy



class CodeContext:
    def __init__(self):
        self.known_files = []

    def copy_src(self) -> List[str]:
        dest_dir = artifacts_dir

        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        files_to_copy = get_all_src_files()

        for rel_path in files_to_copy:
            src_path = os.path.join(src_root_dir, rel_path)
            dest_path = os.path.join(dest_dir, rel_path)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(src_path, dest_path)

        self.known_files = files_to_copy
        return self.known_files
