from tree_sitter import Language, Parser
from tree_sitter_python import language as python_language
from tree_sitter_javascript import language as javascript_language
from tree_sitter_typescript import language as typescript_language

# WIP: Wrapper around TreeSitter that takes care of the languages that we want.

# TODO: Add a map between extensions and languages.

class TreeSitterWrapper:
    def __init__(self):
        self.languages = {
            "python": Language(python_language()),
            "javascript": Language(javascript_language()),
            "typescript": Language(typescript_language()),
        }
        self.parsers = {lang: Parser(lang) for lang in self.languages}

    def parse(self, code, language):
        if language not in self.parsers:
            raise ValueError(f"Unsupported language: {language}")

        tree = self.parsers[language].parse(bytes(code, "utf8"))
        return tree

    def query(self, language, query_string):
        if language not in self.languages:
            raise ValueError(f"Unsupported language: {language}")

        return self.languages[language].query(query_string)

    def execute_query(self, tree, query):
        return query.matches(tree.root_node)


# Example usage
if __name__ == "__main__":
    ts_wrapper = TreeSitterWrapper()

    # Example Python code
    python_code = """
def hello_world():
    print("Hello, World!")
    """

    # Parse Python code
    python_tree = ts_wrapper.parse(python_code, "python")

    # Create a query to find function definitions
    python_query = ts_wrapper.query(
        "python", "(function_definition name: (identifier) @function_name)"
    )

    # Execute the query
    matches = ts_wrapper.execute_query(python_tree, python_query)

    # Print results
    for match in matches:
        for capture in match.captures:
            print(f"Found function: {capture.node.text.decode('utf8')}")
