import os
import ast
from constants import artifacts_dir

def get_imports(file_path):
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read())
    
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module if node.module else ''
            for alias in node.names:
                imports.append(f"{module}.{alias.name}")
    
    return imports

def analyze_repository(repo_path):
    dependencies = {}
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                module_name = os.path.splitext(file)[0]
                imports = get_imports(file_path)
                dependencies[module_name] = imports
    
    return dependencies

def main():
    repo_path = str(artifacts_dir)
    print(f"Analyzing directory: {repo_path}")
    
    dependencies = analyze_repository(repo_path)
    
    print("\nModule dependencies:")
    for module, imports in dependencies.items():
        print(f"{module}:")
        for imp in imports:
            print(f"  -> {imp}")
        print()

if __name__ == "__main__":
    main()