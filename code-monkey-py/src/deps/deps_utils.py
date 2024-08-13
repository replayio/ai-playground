import os
from constants import get_artifacts_dir


def resolve_file_path(relative_path: str) -> str:
    return os.path.join(get_artifacts_dir(), relative_path)


def resolve_module_path(module: str) -> str:
    return resolve_file_path(f"{module.replace('.', '/')}.py")


def get_module_name(file_path: str) -> str:
    return os.path.splitext(os.path.relpath(file_path, get_artifacts_dir()))[0].replace(
        "/", "."
    )
