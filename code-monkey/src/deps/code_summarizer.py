from typing import List, Dict, Tuple, Optional, Union
import tokenize
from io import StringIO
import difflib
from tree_sitter import Language, Parser, Node, Tree

CHUNK_SIZE: int = 64  # Maximum size for the content field

class CodeSummarizer:
    def __init__(self, max_chunk_size: int = CHUNK_SIZE, language: str = 'python') -> None:
        self.max_chunk_size: int = max_chunk_size
        self.language: str = language
        self.parser: Parser = self._setup_parser()

    def _setup_parser(self) -> Parser:
        PY_LANGUAGE: Language = Language('path/to/your/tree-sitter-python.so', 'python')
        parser: Parser = Parser()
        parser.set_language(PY_LANGUAGE)
        return parser

    def chunk_code(self, code: str, filename: str) -> List[Dict[str, Union[str, Tuple[int, int]]]]:
        tree: Tree = self.parser.parse(bytes(code, "utf8"))
        chunks: List[Dict[str, Union[str, Tuple[int, int]]]] = self._chunk_node(tree.root_node, code, filename)
        for chunk in chunks:
            content_length: int = len(chunk['content']) - len(f"```python\n{filename}\n") - 4
            assert content_length <= self.max_chunk_size, f"Content exceeds max length: {chunk['content']}"
        return chunks

    def _chunk_node(self, node: Node, full_code: str, filename: str, file_offset: int = 0) -> List[Dict[str, Union[str, Tuple[int, int]]]]:
        chunks: List[Dict[str, Union[str, Tuple[int, int]]]] = []
        node_code: str = full_code[node.start_byte:node.end_byte]
        
        if self._should_summarize(node):
            summary: str = self._summarize_node(node, full_code)
            chunks.append(self._create_chunk(node, summary, filename, file_offset))
            for child in node.children:
                chunks.extend(self._chunk_node(child, full_code, filename, file_offset + node.start_byte))
        elif len(node_code) <= self.max_chunk_size:
            chunks.append(self._create_chunk(node, node_code, filename, file_offset))
        else:
            # Split large non-summarized nodes into smaller chunks
            for i in range(0, len(node_code), self.max_chunk_size):
                chunk: str = node_code[i:i+self.max_chunk_size]
                chunks.append(self._create_chunk(node, chunk, filename, file_offset + i))
        
        return chunks

    def _should_summarize(self, node: Node) -> bool:
        return node.type in ['module', 'function_definition', 'class_definition', 'enum_definition']

    def _summarize_node(self, node: Node, full_code: str) -> str:
        if node.type == 'module':
            return self._summarize_module(node, full_code)
        elif node.type == 'function_definition':
            return self._summarize_function(node, full_code)
        elif node.type == 'class_definition':
            return self._summarize_class(node, full_code)
        elif node.type == 'enum_definition':
            return self._summarize_enum(node, full_code)
        else:
            raise ValueError(f"Unexpected node type for summarization: {node.type}")

    def _summarize_module(self, node: Node, full_code: str) -> str:
        funcs: List[str] = [self._get_node_name(child, full_code) for child in node.children if child.type == "function_definition"]
        classes: List[str] = [self._get_node_name(child, full_code) for child in node.children if child.type == "class_definition"]
        return self._truncate(f"Module: functions={','.join(funcs)}; classes={','.join(classes)}")

    def _summarize_function(self, node: Node, full_code: str) -> str:
        name: str = self._get_node_name(node, full_code)
        params: List[str] = self._get_function_params(node, full_code)
        return self._truncate(f"def {name}({', '.join(params)})")

    def _summarize_class(self, node: Node, full_code: str) -> str:
        name: str = self._get_node_name(node, full_code)
        methods: List[str] = [self._get_node_name(child, full_code) for child in node.children if child.type == "function_definition"]
        return self._truncate(f"class {name}: methods={', '.join(methods)}")

    def _summarize_enum(self, node: Node, full_code: str) -> str:
        name: str = self._get_node_name(node, full_code)
        return self._truncate(f"enum {name}")

    def _get_node_name(self, node: Node, full_code: str) -> str:
        for child in node.children:
            if child.type == "identifier":
                return full_code[child.start_byte:child.end_byte]
        return "unnamed"

    def _get_function_params(self, node: Node, full_code: str) -> List[str]:
        params_node: Optional[Node] = next((child for child in node.children if child.type == "parameters"), None)
        if params_node:
            return [full_code[param.start_byte:param.end_byte] for param in params_node.children if param.type == "identifier"]
        return []

    def _truncate(self, summary: str) -> str:
        if len(summary) > self.max_chunk_size:
            return summary[:self.max_chunk_size-3] + "..."
        return summary

    def _create_chunk(self, node: Node, content: str, filename: str, file_offset: int) -> Dict[str, Union[str, Tuple[int, int]]]:
        return {
            'content': f"```python\n{filename}\n{content}\n```",
            'index': (file_offset, file_offset + len(content))
        }

# Example usage with diff assertion
if __name__ == "__main__":
    code: str = """
def greet(name):
    """Greet a person."""
    return f"Hello, {name}!"

class Calculator:
    def __init__(self, initial=0):
        self.value = initial

    def add(self, x):
        """Add a number to the current value."""
        self.value += x
        return self

def complex_function(start, end):
    """Perform a complex calculation."""
    result = 0
    for i in range(start, end):
        if i % 2 == 0:
            result += i
        else:
            result -= i
    return result

# Some additional code
print("This is a long string.")
x, y = 10, 20
z = x + y
"""

    chunker: CodeSummarizer = CodeSummarizer()
    actual_chunks: List[Dict[str, Union[str, Tuple[int, int]]]] = chunker.chunk_code(code, "example.py")
    
    # Expected chunks based on the new implementation
    expected_chunks: List[Dict[str, Union[str, Tuple[int, int]]]] = [
        {'content': '```python\nexample.py\nModule: functions=greet,complex_function; classes=Calculator\n```', 'index': (0, 64)},
        {'content': '```python\nexample.py\ndef greet(name)\n```', 'index': (1, 16)},
        {'content': '```python\nexample.py\n    """Greet a person."""\n    return f"Hello, {name}!"\n```', 'index': (17, 73)},
        {'content': '```python\nexample.py\nclass Calculator: methods=__init__, add\n```', 'index': (75, 116)},
        {'content': '```python\nexample.py\ndef __init__(self, initial=0):\n        self.value = initial\n```', 'index': (121, 180)},
        {'content': '```python\nexample.py\ndef add(self, x):\n        """Add a number to the current value."""\n```', 'index': (186, 252)},
        {'content': '```python\nexample.py\n        self.value += x\n        return self\n```', 'index': (257, 300)},
        {'content': '```python\nexample.py\ndef complex_function(start, end)\n```', 'index': (302, 335)},
        {'content': '```python\nexample.py\n    """Perform a complex calculation."""\n    result = 0\n```', 'index': (340, 397)},
        {'content': '```python\nexample.py\n    for i in range(start, end):\n        if i % 2 == 0:\n```', 'index': (402, 461)},
        {'content': '```python\nexample.py\n            result += i\n        else:\n            result -= i\n```', 'index': (466, 529)},
        {'content': '```python\nexample.py\n    return result\n```', 'index': (534, 551)},
        {'content': '```python\nexample.py\n# Some additional code\nprint("This is a long string.")\n```', 'index': (553, 613)},
        {'content': '```python\nexample.py\nx, y = 10, 20\nz = x + y\n```', 'index': (614, 637)}
    ]

    def compare_chunks(actual: List[Dict[str, Union[str, Tuple[int, int]]]], expected: List[Dict[str, Union[str, Tuple[int, int]]]]) -> Optional[str]:
        if len(actual) != len(expected):
            return f"Number of chunks mismatch. Actual: {len(actual)}, Expected: {len(expected)}"
        
        for i, (act, exp) in enumerate(zip(actual, expected)):
            if act['content'] != exp['content']:
                return f"Content mismatch in chunk {i+1}. Actual: {act['content']}, Expected: {exp['content']}"
            
            if act['index'] != exp['index']:
                return f"Index mismatch in chunk {i+1}. Actual: {act['index']}, Expected: {exp['index']}"
            
            content_length: int = len(act['content']) - len("```python\nexample.py\n") - 4
            assert content_length <= CHUNK_SIZE, f"Chunk {i+1} content exceeds max length: {act['content']}"
        
        return None

    diff_result: Optional[str] = compare_chunks(actual_chunks, expected_chunks)
    assert diff_result is None, f"Chunks do not match:\n{diff_result}"
    print("All chunks match the expected output and are within the maximum length.")
    
    # Print actual chunks for visual inspection
    print("\nActual Chunks:")
    for i, chunk in enumerate(actual_chunks):
        print(f"\nChunk {i + 1}:")
        print(f"Index: {chunk['index']}")
        print(f"Content:")
        print(chunk['content'])
        content_length: int = len(chunk['content']) - len("```python\nexample.py\n") - 4
        print(f"Content length (without markdown and filename): {content_length}")