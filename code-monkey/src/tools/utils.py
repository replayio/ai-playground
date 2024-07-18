import os
import shutil
import subprocess
from typing import List, Set
from constants import artifacts_dir, src_dir
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern


def make_file_path(name: str) -> str:
    file_path = os.path.join(artifacts_dir, name)
    if os.path.commonpath([file_path, artifacts_dir]) != artifacts_dir:
        raise ValueError("Access to file outside artifacts directory is not allowed")
    return file_path


def ask_user(prompt: str) -> str:
    print(prompt)
    return input()


def get_file_tree(directory: str, ignore_spec: PathSpec) -> Set[str]:
    relative_paths = set()
    for root, dirs, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, directory)
            if not ignore_spec.match_file(relative_path):
                relative_paths.add(relative_path)
    return relative_paths


def copy_src() -> List[str]:
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

    try:
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, src_dir)
                if not ignore_spec.match_file(rel_path):
                    dest_path = os.path.join(dest_dir, rel_path)
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(src_path, dest_path)
    except Exception as e:
        print(f"Error copying files: {str(e)}")

    return list(get_file_tree(dest_dir, ignore_spec))


def show_diff(original_file: str, modified_file: str) -> str:
    if os.path.exists(original_file) and os.path.exists(modified_file):
        subprocess.run(
            ["code", "--diff", original_file, modified_file],
            capture_output=True,
            text=True,
        )
    elif os.path.exists(modified_file):
        subprocess.run(["code", modified_file], capture_output=True, text=True)
    elif os.path.exists(original_file):
        print("File deleted.")
    else:
        raise Exception(
            f"Could not diff files. Neither file exists: {original_file} and {modified_file}"
        )