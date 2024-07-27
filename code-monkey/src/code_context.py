import os
import shutil
import logging
from typing import List
import pathspec
from constants import get_artifacts_dir, get_root_dir

def get_all_src_files() -> List[str]:
    src_files = []

    root_dir = get_root_dir()

    # Read .gitignore patterns
    gitignore_patterns = [".git"]
    # Check current directory and up to max 3 parent directories until we hit
    # our root dir.
    for i in range(4):
        dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".." for _ in range(i)]))

        gitignore_path = os.path.join(dir_path, ".gitignore")
        logging.debug(f"checking gitignore path {gitignore_path}")
        if os.path.exists(gitignore_path):
            logging.debug("   found it")
            with open(gitignore_path, 'r') as gitignore_file:
                gitignore_patterns.extend(gitignore_file.read().splitlines())

        if (dir_path == root_dir):
            break

    # Create PathSpec object
    ignore_spec = pathspec.GitIgnoreSpec.from_lines(gitignore_patterns)

    for root, dirs, files in os.walk(get_root_dir()):
        for file in files: 
            src_path = os.path.join(root, file)
            rel_path = os.path.relpath(src_path, get_root_dir())
            if not ignore_spec.match_file(rel_path):
                src_files.append(rel_path)
    return src_files



class CodeContext:
    def __init__(self):
        self.known_files = []

    def copy_src(self) -> List[str]:
        dest_dir = get_artifacts_dir()

        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        files_to_copy = get_all_src_files()

        for rel_path in files_to_copy:
            src_path = os.path.join(get_root_dir(), rel_path)
            dest_path = os.path.join(dest_dir, rel_path)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(src_path, dest_path)

        self.known_files = files_to_copy
        return self.known_files

if __name__ == "__main__":
    for file in get_all_src_files():
        print(file)