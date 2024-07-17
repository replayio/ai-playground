import os
import ast
from typing import Dict, List, Tuple
import graphviz
from pylint import astroid
from constants import src_dir

def get_python_files(directory: str) -> List[str]:
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def parse_file(file_path: str) -> Tuple[str, Dict[str, List[str]]]:
    with open(file_path, 'r') as file:
        content = file.read()
    
    module = astroid.parse(content)
    class_info = {}
    
    for node in module.body:
        if isinstance(node, astroid.ClassDef):
            methods = [m.name for m in node.mymethods()]
            class_info[node.name] = methods
    
    return os.path.basename(file_path), class_info

def generate_uml(files_info: Dict[str, Dict[str, List[str]]]):
    dot = graphviz.Digraph(comment='UML Diagram')
    dot.attr(rankdir='TB', size='8,8')

    for file, classes in files_info.items():
        with dot.subgraph(name=f'cluster_{file}') as c:
            c.attr(label=file, style='filled', color='lightgrey')
            for class_name, methods in classes.items():
                class_node = f'{file}_{class_name}'
                label = f'{{{class_name}|{"|".join(methods)}}}'
                c.node(class_node, label, shape='record')

    dot.render('uml_diagram', format='png', cleanup=True)
    print("UML diagram generated: uml_diagram.png")

def main():
    python_files = get_python_files(src_dir)
    files_info = {}
    
    for file in python_files:
        file_name, class_info = parse_file(file)
        files_info[file_name] = class_info
    
    generate_uml(files_info)

if __name__ == '__main__':
    main()