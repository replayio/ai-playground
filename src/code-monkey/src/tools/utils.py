import os
import shutil
import subprocess
from typing import List, Set
from constants import artifacts_dir, src_dir


def make_file_path(name: str) -> str:
    file_path = os.path.join(artifacts_dir, name)
    if os.path.commonpath([file_path, artifacts_dir]) != artifacts_dir:
        raise ValueError("Access to file outside artifacts directory is not allowed")
    return file_path


def ask_user(prompt: str) -> str:
    print(prompt)
    return input()


def get_file_tree(directory: str) -> Set[str]:
    relative_paths = set()
    for root, dirs, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, directory)
            relative_paths.add(relative_path)
    return relative_paths


def copy_src() -> List[str]:
    dest_dir = artifacts_dir

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    try:
        shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)
    except Exception as e:
        print(f"Directory not copied. Error: {str(e)}")

    return list(get_file_tree(dest_dir))

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
