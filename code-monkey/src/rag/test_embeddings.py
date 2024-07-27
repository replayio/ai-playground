import unittest
from rag.embeddings import TreeSitterTextSplitter
from tree_sitter_typescript import language_typescript, language_tsx

class TestTreeSitterTextSplitter(unittest.TestCase):

    def setUp(self):
        self.python_file = "/home/ubuntu/ai-playground/code-monkey/src/tests/sample_files/sample.py"
        self.javascript_file = "/home/ubuntu/ai-playground/code-monkey/src/tests/sample_files/sample.js"
        self.typescript_file = "/home/ubuntu/ai-playground/code-monkey/src/tests/sample_files/sample.ts"
        self.text_file = "/home/ubuntu/ai-playground/code-monkey/src/tests/sample_files/sample.txt"
        self.typescript_language = language_typescript
        self.tsx_language = language_tsx

    def test_split_python_file(self):
        splitter = TreeSitterTextSplitter(language='python', chunk_size=128, top_k=3)
        with open(self.python_file, 'r') as f:
            content = f.read()
        chunks = splitter.split_text(content)
        self.assertGreater(len(chunks), 0)
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 128)

        # Check if the greet function is in the chunks
        self.assertTrue(any("def greet(name):" in chunk for chunk in chunks))
        self.assertTrue(any('return f"Hello, {name}!"' in chunk for chunk in chunks))

        # Check if the Calculator class is in the chunks
        self.assertTrue(any("class Calculator:" in chunk for chunk in chunks))
        self.assertTrue(any("def add(self, a, b):" in chunk for chunk in chunks))
        self.assertTrue(any("def subtract(self, a, b):" in chunk for chunk in chunks))

        # Check if the main block is in the chunks
        self.assertTrue(any('print(greet("World"))' in chunk for chunk in chunks))

    def test_split_javascript_file(self):
        splitter = TreeSitterTextSplitter(language='javascript', chunk_size=128, top_k=3)
        with open(self.javascript_file, 'r') as f:
            content = f.read()
        chunks = splitter.split_text(content)
        self.assertGreater(len(chunks), 0)
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 128)

        # Check if the greet function is in any chunk
        self.assertTrue(any("function greet(name)" in chunk for chunk in chunks))
        self.assertTrue(any("return `Hello, ${name}!`;" in chunk for chunk in chunks))

        # Check if the Calculator class is in any chunk
        self.assertTrue(any("class Calculator" in chunk for chunk in chunks))
        self.assertTrue(any("add(a, b) {" in chunk for chunk in chunks))
        self.assertTrue(any("subtract(a, b) {" in chunk for chunk in chunks))

        # Check if the main code is in any chunk
        self.assertTrue(any('console.log(greet("World"));' in chunk for chunk in chunks))

    def test_split_typescript_file(self):
        splitter = TreeSitterTextSplitter(language='typescript', chunk_size=128, top_k=3)
        with open(self.typescript_file, 'r') as f:
            content = f.read()
        chunks = splitter.split_text(content)
        self.assertGreater(len(chunks), 0)
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 128)

        # Check if the greet function is in any chunk
        self.assertTrue(any("function greet" in chunk for chunk in chunks))
        self.assertTrue(any("function greet(name: string): string {" in chunk for chunk in chunks))
        self.assertTrue(any("return `Hello, ${name}!`;" in chunk for chunk in chunks))

        # Check if the Calculator class is in any chunk
        self.assertTrue(any("class Calculator" in chunk for chunk in chunks))
        self.assertTrue(any("add(a: number, b: number): number {" in chunk for chunk in chunks))
        self.assertTrue(any("subtract(a: number, b: number): number {" in chunk for chunk in chunks))

        # Check if the main execution is in a chunk
        self.assertTrue(any('console.log(greet("World"));' in chunk for chunk in chunks))

    def test_split_default_text(self):
        splitter = TreeSitterTextSplitter(language='text', chunk_size=64, top_k=3)
        with open(self.text_file, 'r') as f:
            content = f.read()
        chunks = splitter.split_text(content)
        self.assertGreater(len(chunks), 0)
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 64)
        self.assertTrue(any("This is a sample text file." in chunk for chunk in chunks))
        self.assertTrue(any("It contains multiple lines of text." in chunk for chunk in chunks))
        self.assertTrue(any("Each line will be used to test the default chunker." in chunk for chunk in chunks))
        self.assertTrue(any("The chunker should split the text into chunks of the specified size." in chunk for chunk in chunks))
        self.assertTrue(any("This is the last line of the sample text file." in chunk for chunk in chunks))

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

if __name__ == '__main__':
    unittest.main()
