import tree_sitter
from tree_sitter import Language, Parser
from deepdiff import DeepDiff
from typing import Dict, Set, Any


# Based on https://claude.ai/chat/ab75e38c-0b20-4532-bf82-1446776bd273
class PDG:
    def __init__(self, graph: Dict[str, Any]):
        self.graph = graph

    def get_all_dependencies(self, fully_qualified_name: str) -> Set[str]:
        dependencies = set()
        parts = fully_qualified_name.split(".")

        if len(parts) > 2 and parts[-2] == "methods":
            # It's a method
            class_name = ".".join(parts[:-2])
            method_name = parts[-1]
            method_data = self.graph[class_name]["methods"][
                f"{class_name}.{method_name}"
            ]
            dependencies.update(self._get_dependencies_recursive(method_data["graph"]))
            dependencies.update(method_data["inputs"])
        elif fully_qualified_name in self.graph:
            # It's a top-level entity
            if (
                isinstance(self.graph[fully_qualified_name], dict)
                and "graph" in self.graph[fully_qualified_name]
            ):
                dependencies.update(
                    self._get_dependencies_recursive(
                        self.graph[fully_qualified_name]["graph"]
                    )
                )
            else:
                dependencies.update(self.graph[fully_qualified_name])

        return dependencies

    def _get_dependencies_recursive(self, graph: Dict[str, Set[str]]) -> Set[str]:
        all_deps = set()
        for deps in graph.values():
            all_deps.update(deps)
            for dep in deps:
                if dep in graph:
                    all_deps.update(self._get_dependencies_recursive({dep: graph[dep]}))
        return all_deps


class PDGBuilder:
    def __init__(self):
        PY_LANGUAGE = Language("build/my-languages.so", "python")
        self.parser = Parser()
        self.parser.set_language(PY_LANGUAGE)

    def build(self, code: str, module_name: str) -> PDG:
        tree = self.parser.parse(bytes(code, "utf8"))
        graph = self._extract_pdg(tree.root_node, code, module_name)
        return PDG(graph)

    def _extract_pdg(
        self,
        node,
        source_code,
        module_name,
        dependencies=None,
        current_var=None,
        function_name=None,
        class_name=None,
    ):
        if dependencies is None:
            dependencies = {}

        if node.type == "class_definition":
            name = node.child_by_field_name("name")
            body = node.child_by_field_name("body")

            if name and body:
                class_name = (
                    f"{module_name}.{source_code[name.start_byte:name.end_byte]}"
                )
                dependencies[class_name] = {
                    "methods": {},
                    "attributes": set(),
                    "self": set(),
                }
                self._extract_pdg(
                    body, source_code, module_name, dependencies, None, None, class_name
                )

        elif node.type == "function_definition":
            name = node.child_by_field_name("name")
            params = node.child_by_field_name("parameters")
            body = node.child_by_field_name("body")

            if name and params and body:
                func_name = source_code[name.start_byte : name.end_byte]
                if class_name:
                    full_func_name = f"{class_name}.{func_name}"
                    dependencies[class_name]["methods"][full_func_name] = {
                        "inputs": [],
                        "graph": {},
                        "outputs": set(),
                    }
                    func_data = dependencies[class_name]["methods"][full_func_name]
                else:
                    full_func_name = f"{module_name}.{func_name}"
                    dependencies[full_func_name] = {
                        "inputs": [],
                        "graph": {},
                        "outputs": set(),
                    }
                    func_data = dependencies[full_func_name]

                for param in params.children:
                    if param.type == "identifier":
                        param_name = source_code[param.start_byte : param.end_byte]
                        if param_name == "self" and class_name:
                            full_param_name = f"{class_name}.self"
                        else:
                            full_param_name = f"{full_func_name}.{param_name}"
                        func_data["inputs"].append(full_param_name)
                        func_data["graph"][full_param_name] = set()

                self._extract_pdg(
                    body,
                    source_code,
                    module_name,
                    func_data["graph"],
                    None,
                    full_func_name,
                    class_name,
                )

        elif node.type == "assignment":
            left = node.child_by_field_name("left")
            right = node.child_by_field_name("right")

            if left and right:
                left_var = source_code[left.start_byte : left.end_byte]
                if class_name and left_var.startswith("self."):
                    left_var = f"{class_name}.{left_var[5:]}"
                    dependencies[class_name]["attributes"].add(left_var.split(".")[-1])
                elif function_name:
                    left_var = f"{function_name}.{left_var}"
                elif not class_name:
                    left_var = f"{module_name}.{left_var}"
                if left_var not in dependencies:
                    dependencies[left_var] = set()
                self._extract_pdg(
                    right,
                    source_code,
                    module_name,
                    dependencies,
                    left_var,
                    function_name,
                    class_name,
                )

        elif node.type == "identifier":
            var_name = source_code[node.start_byte : node.end_byte]
            if current_var:
                if var_name == "self" and class_name:
                    full_var_name = f"{class_name}.self"
                elif function_name:
                    full_var_name = f"{function_name}.{var_name}"
                elif class_name:
                    full_var_name = f"{class_name}.{var_name}"
                else:
                    full_var_name = f"{module_name}.{var_name}"
                dependencies[current_var].add(full_var_name)

        elif node.type == "attribute":
            obj = node.child_by_field_name("object")
            attr = node.child_by_field_name("attribute")
            if obj and attr:
                obj_name = source_code[obj.start_byte : obj.end_byte]
                attr_name = source_code[attr.start_byte : attr.end_byte]
                if obj_name == "self" and class_name:
                    full_name = f"{class_name}.{attr_name}"
                else:
                    # Check if the object is a known class in the module
                    potential_class = f"{module_name}.{obj_name}"
                    if (
                        potential_class in dependencies
                        and attr_name in dependencies[potential_class]["attributes"]
                    ):
                        full_name = f"{potential_class}.{attr_name}"
                    else:
                        if function_name:
                            obj_name = f"{function_name}.{obj_name}"
                        full_name = f"{obj_name}.{attr_name}"
                if current_var:
                    dependencies[current_var].add(full_name)

        elif node.type == "if_statement":
            condition = node.child_by_field_name("condition")
            consequence = node.child_by_field_name("consequence")
            alternative = node.child_by_field_name("alternative")

            if condition:
                self._extract_pdg(
                    condition,
                    source_code,
                    module_name,
                    dependencies,
                    current_var,
                    function_name,
                    class_name,
                )
            if consequence:
                self._extract_pdg(
                    consequence,
                    source_code,
                    module_name,
                    dependencies,
                    current_var,
                    function_name,
                    class_name,
                )
            if alternative:
                self._extract_pdg(
                    alternative,
                    source_code,
                    module_name,
                    dependencies,
                    current_var,
                    function_name,
                    class_name,
                )

        elif node.type == "call":
            function = node.child_by_field_name("function")
            arguments = node.child_by_field_name("arguments")

            if function and arguments:
                func_name = source_code[function.start_byte : function.end_byte]
                if "." not in func_name:
                    if function_name:
                        func_name = f"{function_name}.{func_name}"
                    elif not class_name:
                        func_name = f"{module_name}.{func_name}"
                if current_var:
                    dependencies[current_var].add(func_name)
                for arg in arguments.children:
                    if arg.type != "argument_list":
                        self._extract_pdg(
                            arg,
                            source_code,
                            module_name,
                            dependencies,
                            current_var,
                            function_name,
                            class_name,
                        )

        elif node.type == "return_statement":
            child = node.child_by_field_name("value")
            if child and function_name:
                temp_var = f"{function_name}._temp_return"
                dependencies[temp_var] = set()
                self._extract_pdg(
                    child,
                    source_code,
                    module_name,
                    dependencies,
                    temp_var,
                    function_name,
                    class_name,
                )
                if class_name:
                    dependencies[class_name]["methods"][function_name][
                        "outputs"
                    ].update(dependencies[temp_var])
                else:
                    dependencies[function_name]["outputs"].update(
                        dependencies[temp_var]
                    )
                del dependencies[temp_var]

        for child in node.children:
            self._extract_pdg(
                child,
                source_code,
                module_name,
                dependencies,
                current_var,
                function_name,
                class_name,
            )

        return dependencies


# TODO: move this to tests.
if __name__ == "__main__":
    # Example with a module name, class, global variable, and branching logic
    python_code = """
    TAX_RATE = 0.2

    class Employee:
        def __init__(self, name, salary):
            self.name = name
            self.salary = salary

    def calculate_net_income(employee):
        gross_income = employee.salary
        if gross_income > 100000:
            tax_rate = TAX_RATE * 1.1
        else:
            tax_rate = TAX_RATE
        tax = gross_income * tax_rate
        net_income = gross_income - tax
        return net_income
    """

    module_name = "payroll"
    pdg_builder = PDGBuilder()
    pdg = pdg_builder.build(python_code, module_name)

    # Expected result
    expected_pdg = {
        "payroll.TAX_RATE": set(),
        "payroll.Employee": {
            "methods": {
                "payroll.Employee.__init__": {
                    "inputs": [
                        "payroll.Employee.self",
                        "payroll.Employee.__init__.name",
                        "payroll.Employee.__init__.salary",
                    ],
                    "graph": {
                        "payroll.Employee.self": set(),
                        "payroll.Employee.__init__.name": set(),
                        "payroll.Employee.__init__.salary": set(),
                        "payroll.Employee.name": {"payroll.Employee.__init__.name"},
                        "payroll.Employee.salary": {"payroll.Employee.__init__.salary"},
                    },
                    "outputs": set(),
                }
            },
            "attributes": {"name", "salary"},
            "self": set(),
        },
        "payroll.calculate_net_income": {
            "inputs": ["payroll.calculate_net_income.employee"],
            "graph": {
                "payroll.calculate_net_income.employee": set(),
                "payroll.calculate_net_income.gross_income": {"payroll.Employee.salary"},
                "payroll.calculate_net_income.tax_rate": {"payroll.TAX_RATE"},
                "payroll.calculate_net_income.tax": {
                    "payroll.calculate_net_income.gross_income",
                    "payroll.calculate_net_income.tax_rate",
                },
                "payroll.calculate_net_income.net_income": {
                    "payroll.calculate_net_income.gross_income",
                    "payroll.calculate_net_income.tax",
                },
            },
            "outputs": {"payroll.calculate_net_income.net_income"},
        },
    }

    # Compare PDGs using DeepDiff with verbose_level=2 for detailed differences
    diff = DeepDiff(pdg.graph, expected_pdg, ignore_order=True, verbose_level=2)

    # Assert the result
    assert not diff, f"PDG does not match expected result. Differences:\n{diff.pretty()}"

    # Test get_all_dependencies method for payroll.calculate_net_income.net_income
    all_deps = pdg.get_all_dependencies("payroll.calculate_net_income.net_income")
    expected_deps = {
        "payroll.calculate_net_income.gross_income",
        "payroll.calculate_net_income.tax",
        "payroll.Employee.salary",
        "payroll.calculate_net_income.tax_rate",
        "payroll.TAX_RATE",
    }

    assert (
        all_deps == expected_deps
    ), f"Dependencies mismatch for net_income. Got: {all_deps}, Expected: {expected_deps}"

