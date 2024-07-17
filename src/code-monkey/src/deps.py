from pylint.pyreverse.main import Run
from pylint.pyreverse.inspector import Linker
from pylint.pyreverse.utils import insert_default_options
from astroid import MANAGER
from typing import List, Tuple
from constants import artifacts_dir


def analyze_repository(repo_path: str) -> List[Tuple[str, str]]:
    # Prepare command-line style arguments for pyreverse
    args = ['-o', 'dot', '-p', 'myproject', repo_path]
    
    # Insert default options
    insert_default_options(args)
    
    # Run pyreverse analysis
    config = Run(args, exit=False).config
    project = config.project
    
    # Use the Linker to get dependencies
    linker = Linker(project)
    linker.visit(project)
    
    # Extract dependencies
    dependencies = []
    for module in project.modules():
        for dep in module.depends:
            dependencies.append((module.name, dep.name))
    
    return dependencies

def main():
    repo_path = artifacts_dir

    # Clear astroid cache to ensure fresh analysis
    MANAGER.astroid_cache.clear()
    
    dependencies = analyze_repository(repo_path)

    print("Module dependencies:")
    for dep in dependencies:
        print(f"{dep[0]} -> {dep[1]}")

if __name__ == "__main__":
    main()
