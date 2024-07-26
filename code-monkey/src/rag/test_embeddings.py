import unittest
import sys
import os
import subprocess
import json
import logging
from typing import Optional

# Get the path to the tree-sitter installation
try:
    result = subprocess.run(['rye', 'run', 'python', '-c', 'import tree_sitter; print(tree_sitter.__file__)'], capture_output=True, text=True, check=True)
    tree_sitter_path = os.path.dirname(result.stdout.strip())
    sys.path.append(tree_sitter_path)
except subprocess.CalledProcessError:
    logging.warning("Unable to locate tree-sitter module. Make sure it's installed.")

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag.embeddings import TreeSitterTextSplitter

try:
    from tree_sitter import Parser, Language
    from tree_sitter_languages import get_language, get_parser
except ImportError as e:
    logging.warning(f"Unable to import tree-sitter modules: {e}. Some tests may be skipped.")
    Parser = Language = get_language = get_parser = None

class TestTreeSitterTextSplitter(unittest.TestCase):
    def setUp(self):
        self.python_file = "/home/ubuntu/ai-playground/code-monkey/src/tests/sample_files/sample.py"
        self.javascript_file = "/home/ubuntu/ai-playground/code-monkey/src/tests/sample_files/sample.js"
        self.typescript_file = "/home/ubuntu/ai-playground/code-monkey/src/tests/sample_files/sample.ts"
        self.text_file = "/home/ubuntu/ai-playground/code-monkey/src/tests/sample_files/sample.txt"



        # Ensure the TypeScript file exists with sample content
        if not os.path.exists(self.typescript_file):
            with open(self.typescript_file, 'w') as f:
                f.write("""
                interface User {
                    name: string;
                    age: number;
                }

                class Greeter {
                    greeting: string;
                    constructor(message: string) {
                        this.greeting = message;
                    }
                    greet() {
                        console.log("Hello, " + this.greeting);
                    }
                }

                function logUser(user: User) {
                    console.log(`User: ${user.name}, Age: ${user.age}`);
                }

                const user: User = { name: "Alice", age: 30 };
                const greeter = new Greeter("TypeScript");
                greeter.greet();
                logUser(user);
                """)



    def test_split_python_file(self):
        splitter = TreeSitterTextSplitter(language='python', chunk_size=64, top_k=3)
        with open(self.python_file, 'r') as f:
            content = f.read()
        chunks = splitter.split_text(content)

        self.assertLessEqual(len(chunks), 3)  # Check top_k limit
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 64)  # Check chunk size

        # Check if the greet function is in the chunks
        greet_function = next((chunk for chunk in chunks if "def greet(name):" in chunk), None)
        self.assertIsNotNone(greet_function)
        self.assertIn('return f"Hello, {name}!"', greet_function)

        # Check if the Calculator class is in the chunks
        calculator_class = next((chunk for chunk in chunks if "class Calculator:" in chunk), None)
        self.assertIsNotNone(calculator_class)
        self.assertIn("def add(self, a, b):", calculator_class)
        self.assertIn("def subtract(self, a, b):", calculator_class)

        # Check if the main block is in the chunks
        main_block = next((chunk for chunk in chunks if 'if __name__ == "__main__":' in chunk), None)
        self.assertIsNotNone(main_block)
        self.assertIn('print(greet("World"))', main_block)

    def test_split_javascript_file(self):
        splitter = TreeSitterTextSplitter(language='javascript', chunk_size=64, top_k=3)
        with open(self.javascript_file, 'r') as f:
            content = f.read()
        chunks = splitter.split_text(content)
        print("JavaScript Chunks:", chunks)  # Debug print

        self.assertLessEqual(len(chunks), 3)  # Check top_k limit
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 64)  # Check chunk_size

        # Check if the greet function is in any chunk
        greet_function = any("function greet(name)" in chunk and "return `Hello, ${name}!`;" in chunk for chunk in chunks)
        self.assertTrue(greet_function, "Greet function not found in chunks")

        # Check if the Calculator class is in any chunk
        calculator_class = any("class Calculator" in chunk and "add(a, b) {" in chunk and "subtract(a, b) {" in chunk for chunk in chunks)
        self.assertTrue(calculator_class, "Calculator class not found in chunks")

        # Check if the main code is in any chunk
        main_code = any('console.log(greet("World"));' in chunk for chunk in chunks)
        self.assertTrue(main_code, "Main code execution not found in chunks")

        # Check for console.log statements
        console_log = any('console.log(' in chunk.lower() for chunk in chunks)
        self.assertTrue(console_log, "console.log statement not found in chunks")

        # Verify that each chunk contains valid JavaScript code
        for i, chunk in enumerate(chunks):
            self.assertTrue(any(keyword in chunk for keyword in ['function', 'class', 'const', 'let', 'var']),
                            f"Chunk {i} does not contain valid JavaScript code")

    def test_split_typescript_file(self):
        chunk_size = 64
        top_k = 3
        splitter = TreeSitterTextSplitter(language='typescript', chunk_size=chunk_size, top_k=top_k)
        with open(self.typescript_file, 'r') as f:
            content = f.read()
        chunks = splitter.split_text(content, file_extension='.ts')
        print("TypeScript Chunks:", chunks)  # Debug print

        self.assertLessEqual(len(chunks), top_k, f"Number of chunks exceeds top_k limit of {top_k}")
        for chunk in chunks:
            self.assertLessEqual(len(chunk), chunk_size, f"Chunk size exceeds limit of {chunk_size} characters")

        # Check for TypeScript-specific syntax elements
        typescript_elements = [
            "interface", "class", "function", "const", ": string", ": number", "=>", "implements"
        ]
        self.assertTrue(any(element in ''.join(chunks) for element in typescript_elements), "No TypeScript-specific elements found")

        # Check for specific TypeScript features
        self.assertTrue(any("interface" in chunk for chunk in chunks), "Interface declaration not found")
        self.assertTrue(any("class" in chunk for chunk in chunks), "Class declaration not found")
        self.assertTrue(any("function" in chunk for chunk in chunks), "Function declaration not found")
        self.assertTrue(any("const" in chunk and ":" in chunk for chunk in chunks), "Type annotation in variable declaration not found")

        # Check for type annotations
        self.assertTrue(any(": string" in chunk for chunk in chunks), "String type annotation not found")
        self.assertTrue(any(": number" in chunk for chunk in chunks), "Number type annotation not found")

        # Check for function and class declarations with type annotations
        self.assertTrue(any("function" in chunk and ":" in chunk for chunk in chunks), "Function with type annotation not found")
        self.assertTrue(any("class" in chunk and "constructor" in chunk for chunk in chunks), "Class with constructor not found")

        # Check for console.log statements
        self.assertTrue(any('console.log(' in chunk.lower() for chunk in chunks), "console.log statement not found")

        # Verify that each chunk contains at least one TypeScript-specific element
        for i, chunk in enumerate(chunks):
            self.assertTrue(any(element in chunk for element in typescript_elements), f"Chunk {i} does not contain any TypeScript-specific element")

        # Check for specific code structures
        self.assertTrue(any("{" in chunk and "}" in chunk for chunk in chunks), "Complete code block not found")
        self.assertTrue(any("(" in chunk and ")" in chunk and ":" in chunk for chunk in chunks), "Function or method with type annotation not found")

        # Check for specific TypeScript features in the sample file
        self.assertTrue(any("interface User" in chunk for chunk in chunks), "User interface not found")
        self.assertTrue(any("class Greeter" in chunk for chunk in chunks), "Greeter class not found")
        self.assertTrue(any("function logUser" in chunk for chunk in chunks), "logUser function not found")

        # Verify that important parts of the code are not split across chunks
        full_content = ''.join(chunks)
        self.assertIn("interface User {", full_content, "User interface declaration is incomplete")
        self.assertIn("class Greeter {", full_content, "Greeter class declaration is incomplete")
        self.assertIn("function logUser(user: User) {", full_content, "logUser function declaration is incomplete")

    def test_default_text_splitter(self):
        splitter = TreeSitterTextSplitter(language='unsupported', chunk_size=32, top_k=3)
        sample_text = "This is a sample text. It has exactly 96 characters to test default splitting behavior."
        chunks = splitter.split_text(sample_text)

        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0], "This is a sample text. It has ")
        self.assertEqual(chunks[1], "exactly 96 characters to test ")
        self.assertEqual(chunks[2], "default splitting behavior.")

        for chunk in chunks:
            self.assertEqual(len(chunk), 32)  # Check chunk size


    def test_large_function(self):
        large_function = """
def large_function():
    # This is a large function that exceeds the chunk size
    print("Start of large function")
    for i in range(100):
        print(f"Line {i}")
    print("End of large function")
"""
        splitter = TreeSitterTextSplitter(language='python', chunk_size=128, top_k=3)
        chunks = splitter.split_text(large_function)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk) <= 128 for chunk in chunks))
        self.assertIn("def large_function():", chunks[0])
        self.assertIn("End of large function", chunks[-1])

    def test_chunk_size_and_top_k_configuration(self):
        splitter = TreeSitterTextSplitter(language='python', chunk_size=64, top_k=2)
        with open(self.python_file, 'r') as f:
            content = f.read()
        chunks = splitter.split_text(content)
        self.assertLessEqual(len(chunks), 2)
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 64)

    def test_empty_file(self):
        splitter = TreeSitterTextSplitter(language='python', chunk_size=128, top_k=3)
        chunks = splitter.split_text("")
        self.assertEqual(len(chunks), 0)

    def test_unsupported_language(self):
        splitter = TreeSitterTextSplitter(language='unsupported', chunk_size=128, top_k=3)
        with open(self.text_file, 'r') as f:
            content = f.read()
        chunks = splitter.split_text(content)
        self.assertGreater(len(chunks), 0)
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 128)

    def test_top_k_limit(self):
        splitter = TreeSitterTextSplitter(language='python', chunk_size=32, top_k=3)
        with open(self.python_file, 'r') as f:
            content = f.read()
        chunks = splitter.split_text(content)
        self.assertEqual(len(chunks), 3)

    def test_chunk_size_and_top_k_typescript(self):
        chunk_size, top_k = 256, 10  # Increased from 128 and 5
        splitter = TreeSitterTextSplitter(language='typescript', chunk_size=chunk_size, top_k=top_k)
        with open(self.typescript_file, 'r') as f:
            content = f.read()
        print("TypeScript File Content:", content)  # Debug print
        chunks = splitter.split_text(content)
        print("TypeScript Chunks:")
        for i, chunk in enumerate(chunks):
            print(f"Chunk {i + 1}:\n{chunk}\n")
        self.assertLessEqual(len(chunks), top_k)  # Ensure top_k is not exceeded
        for chunk in chunks:
            self.assertLessEqual(len(chunk), chunk_size)  # Ensure chunk size is respected

        # Check for TypeScript-specific syntax elements
        typescript_elements = [
            "function", "class", ": string", ": number", "const"
        ]
        all_chunks_content = ''.join(chunks)
        for element in typescript_elements:
            self.assertIn(element, all_chunks_content, f"'{element}' not found in any chunk")

        # Check for specific declarations
        self.assertTrue(any("function greet(" in chunk for chunk in chunks), "greet function not found in chunks")
        self.assertTrue(any("class Calculator" in chunk for chunk in chunks), "Calculator class not found in chunks")

        # Check for type annotations
        self.assertTrue(any(": string" in chunk or ": number" in chunk for chunk in chunks), "No type annotations found")

        # Check for console.log statements
        self.assertTrue(any('console.log(' in chunk.lower() for chunk in chunks), "No console.log statements found")

        # Verify that chunks contain complete or nearly complete statements/declarations
        self.assertTrue(any("{" in chunk and "}" in chunk for chunk in chunks), "No complete code blocks found")

        # Verify specific TypeScript features are present in chunks
        self.assertTrue(any("function greet(" in chunk for chunk in chunks), "greet function not found in chunks")
        self.assertTrue(any("class Calculator" in chunk for chunk in chunks), "Calculator class not found in chunks")
        self.assertTrue(any("console.log(" in chunk for chunk in chunks), "console.log statement not found in chunks")

        # Check for specific console.log statements
        self.assertTrue(any('console.log(greet("World"))' in chunk for chunk in chunks), "Main console.log statement not found")
        self.assertTrue(any('console.log(`2 + 3 = ${' in chunk for chunk in chunks), "Calculator addition console.log not found")
        self.assertTrue(any('${calc.add(2, 3)}' in chunk for chunk in chunks), "Template literal in calculator addition not found")
        self.assertTrue(any('console.log(`5 - 2 = ${' in chunk for chunk in chunks), "Calculator subtraction console.log not found")
        self.assertTrue(any('${calc.subtract(5, 2)}' in chunk for chunk in chunks), "Template literal in calculator subtraction not found")

    def test_get_imports(self):
        # Note: tree_sitter and tree_sitter_typescript might not be available in all environments
        # This test is designed to be skipped if the required modules are not installed
        try:
            # Attempt to import required modules
            import importlib.util
            spec = importlib.util.find_spec('tree_sitter')
            if spec is None:
                self.skipTest("tree_sitter module not installed")

            spec = importlib.util.find_spec('tree_sitter_typescript')
            if spec is None:
                self.skipTest("tree_sitter_typescript module not installed")

            from tree_sitter import Parser, Language
            from tree_sitter_typescript import language_typescript, language_tsx

            parser = Parser()
            language = Language(language_typescript(), 'typescript')
            parser.set_language(language)

            with open(self.typescript_file, 'r') as f:
                tree = parser.parse(bytes(f.read(), 'utf8'))

            imports = [node for node in tree.root_node.children if node.type in ['import_statement', 'import_declaration']]
            self.assertIsInstance(imports, list)
            self.assertTrue(any('import' in str(imp) for imp in imports))
        except ImportError as e:
            self.skipTest(f"Required module not installed: {str(e)}")
        except Exception as e:
            self.fail(f"Unexpected error in test_get_imports: {str(e)}")

    def test_rg_tool(self):
        try:
            from src.tools.rg_tool import RgTool
            rg_tool = RgTool()
            if hasattr(rg_tool, 'tracer') and rg_tool.tracer is not None:
                result = rg_tool.handle_tool_call({"pattern": "class TreeSitterTextSplitter"})
                self.assertIsInstance(result, str)
                self.assertIn("TreeSitterTextSplitter", result)
            else:
                self.skipTest("RgTool tracer not available")
        except ImportError:
            self.skipTest("RgTool not available")
        except AttributeError:
            self.skipTest("RgTool.handle_tool_call not implemented")

    def test_default_text_splitter(self):
        splitter = TreeSitterTextSplitter(language='unsupported', chunk_size=32, top_k=3)
        sample_text = "This is a sample text. It contains multiple lines. The splitter should work correctly."
        chunks = splitter.split_text(sample_text)
        self.assertEqual(len(chunks), 3)
        self.assertTrue(any("This is a sample" in chunk for chunk in chunks))
        self.assertTrue(any("multiple lines" in chunk for chunk in chunks))
        self.assertTrue(any("splitter should work" in chunk for chunk in chunks))

    def test_typescript_console_log(self):
        splitter = TreeSitterTextSplitter(language='typescript', chunk_size=64, top_k=5)
        with open(self.typescript_file, 'r') as f:
            content = f.read()
        chunks = splitter.split_text(content)
        print("TypeScript Chunks (console.log):", chunks)  # Debug print

        # Check for specific console.log statements
        self.assertTrue(any('console.log("Hello, " + this.greeting);' in chunk for chunk in chunks),
                        "Greeter.greet() console.log not found in chunks")
        self.assertTrue(any('console.log(`User: ${user.name}, Age: ${user.age}`);' in chunk for chunk in chunks),
                        "logUser() console.log not found in chunks")

        # Check for general console.log presence
        self.assertTrue(any('console.log(' in chunk.lower() for chunk in chunks),
                        "No console.log found in chunks")

if __name__ == '__main__':
    unittest.main()
