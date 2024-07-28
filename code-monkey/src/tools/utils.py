import os
import subprocess
import logging
from constants import get_artifacts_dir


def make_file_path(name: str) -> str:
    # abspath here because `name` could start with "../" and escape the
    # artifacts directory
    file_path = os.path.abspath(os.path.join(get_artifacts_dir(), name))
    if os.path.commonpath([file_path, get_artifacts_dir()]) != get_artifacts_dir():
        raise ValueError("Access to file outside artifacts directory is not allowed")
    return file_path


def ask_user(prompt: str) -> str:
    print(prompt)
    return input()


def show_diff(original_file: str, modified_file: str) -> str:
    logging.debug(f"Diffing {original_file} and {modified_file}")
    if os.path.exists(original_file) and os.path.exists(modified_file):
        subprocess.run(
            ["code", "--diff", original_file, modified_file],
        )
    elif os.path.exists(modified_file):
        subprocess.run(["code", modified_file])
    elif os.path.exists(original_file):
        print("File deleted.")
    else:
        raise Exception(
            f"Could not diff files. Neither file exists: {original_file} and {modified_file}"
        )
