import os
from typing import Dict, List
import graphviz
from pylint.pyreverse.main import Run
from pylint.pyreverse.inspector import Project
from constants import src_dir

def get_python_files(directory: str) -> List[str]:
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def parse_files(files: List[str]) -> Project:
    run = Run(files)
    return run.project

def generate_uml(project: Project):
    dot = graphviz.Digraph(comment='UML Diagram')
    dot.attr(rankdir='TB', size='8,8')

    for module in project.modules():
        with dot.subgraph(name=f'cluster_{module.name}') as c:
            c.attr(label=module.name, style='filled', color='lightgrey')
            for klass in module.classes:
                class_node = f'{module.name}_{klass.name}'
                methods = [m.name for m in klass.methods]
                label = f'{{{klass.name}|{"|".join(methods)}}}'
                c.node(class_node, label, shape='record')

    dot.render('uml_diagram', format='png', cleanup=True)
    print("UML diagram generated: uml_diagram.png")

def main():
    python_files = get_python_files(src_dir)
    project = parse_files(python_files)
    generate_uml(project)

if __name__ == '__main__':
    main()