import os
import sys
import re
from typing import List, Dict, Optional, Tuple, Union, Any
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings, VoyageEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.schema import Document
import logging

# Add the directory containing the tree-sitter modules to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

TREE_SITTER_AVAILABLE = False
Tree: Any = None
Node: Any = None
Parser: Any = None
Language: Any = None

try:
    from tree_sitter import Parser, Language, Tree, Node
    import tree_sitter_python
    import tree_sitter_javascript
    import tree_sitter_typescript
    TREE_SITTER_AVAILABLE = True
    logging.info("Successfully imported tree-sitter core modules and language modules.")
except ImportError as e:
    logging.error(f"Failed to import tree_sitter modules. Error: {e}")
    logging.warning("Tree-sitter functionality will be disabled. Some features may be limited.")
    logging.info("Please ensure all required packages are installed using 'rye sync'.")
    logging.info("You may need to run: rye add tree-sitter tree-sitter-languages")
    TREE_SITTER_AVAILABLE = False
    Parser = Language = Tree = Node = None
except Exception as e:
    logging.error(f"Unexpected error importing tree_sitter modules: {e}")
    logging.warning("This might be due to incompatible versions or system-specific issues.")
    logging.info("Please check your installation and system configuration.")
    TREE_SITTER_AVAILABLE = False
    Parser = Language = Tree = Node = None

CHUNK_LENGTH: int = 512




class TreeSitterTextSplitter(RecursiveCharacterTextSplitter):
    def __init__(self, language: str, chunk_size: int = CHUNK_LENGTH, top_k: int = 5) -> None:
        self.language: str = language.lower()
        self._top_k: int = top_k
        self._chunk_size: int = chunk_size
        self.parser = None
        self.ts_language = None

        super().__init__(chunk_size=chunk_size, chunk_overlap=0)

        if not TREE_SITTER_AVAILABLE:
            logging.warning(f"Tree-sitter is not available. Falling back to default text splitting for {self.language}.")
            return

        try:
            self._initialize_parser()
        except Exception as e:
            logging.error(f"Failed to initialize parser for {self.language}: {str(e)}")
            logging.warning(f"Falling back to default text splitting for {self.language}.")

    def _initialize_parser(self):
        try:
            from tree_sitter import Parser
            self.parser = Parser()

            if self.language == 'python':
                from tree_sitter_python import language as python_language
                language = Language(python_language())
            elif self.language == 'javascript':
                from tree_sitter_javascript import language as javascript_language
                language = Language(javascript_language())
            elif self.language == 'typescript':
                try:
                    from tree_sitter_typescript import language_typescript
                    language = Language(language_typescript())
                except ImportError:
                    logging.warning("TypeScript parser not available. Falling back to JavaScript parser.")
                    from tree_sitter_javascript import language as javascript_language
                    language = Language(javascript_language())
            else:
                raise ValueError(f"Unsupported language: {self.language}")

            self.parser.set_language(language)
            logging.info(f"{self.language.capitalize()} parser initialized successfully.")
        except ImportError as e:
            logging.error(f"Failed to import required language module: {str(e)}")
            raise
        except ValueError as e:
            logging.error(f"Error initializing {self.language} parser: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error initializing {self.language} parser: {str(e)}")
            raise

    def split_text(self, text: str, file_extension: str = '') -> List[str]:
        if self.parser is None:
            logging.warning(f"No parser available for language '{self.language}'. Using default split.")
            return self._default_split(text)

        try:
            logging.info(f"Starting to parse and chunk text for language '{self.language}' (length: {len(text)})")
            tree = self.parser.parse(bytes(text, "utf8"))
            logging.debug(f"Parsed tree: {tree.root_node}")
            chunks: List[str] = []

            def traverse_tree(node):
                node_types = [
                    'function_declaration', 'class_declaration', 'interface_declaration',
                    'type_alias_declaration', 'export_statement', 'method_definition',
                    'function', 'class', 'interface', 'type',
                    'function_definition', 'class_definition',
                    'arrow_function', 'variable_declaration', 'lexical_declaration',
                    'import_statement', 'export_statement', 'export_default_declaration',
                    'enum_declaration', 'namespace_declaration',
                    'const_declaration', 'let_declaration',
                    'function_signature', 'method_signature', 'property_signature',
                    'public_field_definition', 'private_field_definition',
                    'ambient_declaration', 'module', 'abstract_class_declaration',
                    'console_log'  # Added console_log to node_types
                ]
                try:
                    if node is None:
                        logging.warning("Encountered None node during tree traversal")
                        return

                    logging.debug(f"Processing node: {node.type}, start: {node.start_byte}, end: {node.end_byte}")
                    if node.type in node_types:
                        chunk = text[node.start_byte:node.end_byte].strip()
                        logging.debug(f"Adding chunk of type '{node.type}': {chunk[:50]}...")
                        if node.type == 'console_log':
                            full_statement = self._capture_full_console_log(node, text)
                            self._add_chunk(full_statement, chunks)
                            logging.debug(f"Added console log chunk: {full_statement}")
                        else:
                            self._add_chunk(chunk, chunks)
                    elif node.type == 'call_expression':
                        call_text = text[node.start_byte:node.end_byte]
                        logging.debug(f"Found call expression: {call_text}")
                        if self._is_console_log(call_text):
                            # Capture the entire console.log statement, including template literals
                            logging.debug(f"Processing console.log. Full call_text: {call_text}")
                            full_statement = self._capture_full_console_log(node, text)
                            self._add_chunk(full_statement, chunks)
                            logging.debug(f"Added console log chunk: {full_statement}")
                    elif node.type == 'program':
                        for child in node.children:
                            traverse_tree(child)
                    else:
                        for child in node.children:
                            traverse_tree(child)
                except AttributeError as ae:
                    logging.error(f"AttributeError in tree traversal: {str(ae)}")
                    logging.debug(f"Node type: {getattr(node, 'type', 'Unknown')}")
                except Exception as e:
                    logging.error(f"Error traversing tree node: {str(e)}")
                    logging.debug(f"Node type: {getattr(node, 'type', 'Unknown')}, Text: {text[getattr(node, 'start_byte', 0):getattr(node, 'end_byte', len(text))]}")

            traverse_tree(tree.root_node)

            # Remove empty chunks and whitespace-only chunks
            chunks = [chunk.strip() for chunk in chunks if chunk.strip()]

            # If no chunks were created, fall back to default splitting
            if not chunks:
                logging.warning(f"No chunks created for {self.language}. Using default split.")
                default_chunks = self._default_split(text)[:self._top_k]
                logging.debug(f"Default split created {len(default_chunks)} chunks.")
                return default_chunks

            logging.info(f"Created {len(chunks)} chunks for {self.language}.")
            logging.debug(f"All chunks before top_k limit: {chunks}")
            if chunks:
                logging.debug(f"First chunk: {chunks[0]}")
                logging.debug(f"Last chunk: {chunks[-1]}")
            return chunks[:self._top_k]
        except Exception as e:
            logging.error(f"Error parsing text for language '{self.language}': {str(e)}")
            logging.debug("Stack trace:", exc_info=True)
            default_chunks = self._default_split(text)[:self._top_k]
            logging.debug(f"Fallback: Default split created {len(default_chunks)} chunks.")
            return default_chunks

    def _capture_full_console_log(self, node, text):
        logging.debug(f"Capturing console.log. Full node text: {text[node.start_byte:node.end_byte]}")

        def balance_delimiters(s):
            stack = []
            for i, char in enumerate(s):
                if char in '({[`':
                    stack.append((char, i))
                elif char in ')}]`':
                    if not stack:
                        logging.warning(f"Unmatched closing delimiter '{char}' at position {i}")
                        return False, i
                    last_open, _ = stack.pop()
                    if (char == ')' and last_open != '(') or \
                       (char == '}' and last_open != '{') or \
                       (char == ']' and last_open != '[') or \
                       (char == '`' and last_open != '`'):
                        logging.warning(f"Mismatched delimiters: '{last_open}' and '{char}' at position {i}")
                        return False, i
                elif char == '$' and i + 1 < len(s) and s[i + 1] == '{':
                    if stack and stack[-1][0] == '`':
                        stack.append(('{', i))
            return len(stack) == 0, len(s)

        end_node = node
        full_statement = ""
        max_depth = 20  # Increased max depth to handle more complex statements
        depth = 0

        while end_node and depth < max_depth:
            if not hasattr(end_node, 'start_byte') or not hasattr(end_node, 'end_byte'):
                logging.warning(f"Invalid node encountered: {end_node}")
                break

            current_text = text[end_node.start_byte:end_node.end_byte]
            if len(full_statement) + len(current_text) > self._chunk_size:
                logging.warning(f"Console.log statement exceeds chunk size: {len(full_statement) + len(current_text)} > {self._chunk_size}")
                # Truncate the current_text to fit within the chunk size
                remaining_space = self._chunk_size - len(full_statement)
                current_text = current_text[:remaining_space]
                full_statement += current_text
                break

            full_statement += current_text

            logging.debug(f"Depth: {depth}, Current node: {end_node.type}, Text: {current_text[:50]}...")

            is_balanced, _ = balance_delimiters(full_statement)
            if is_balanced and full_statement.strip().endswith(';'):
                logging.debug(f"Balanced statement found at depth {depth}")
                break

            if end_node.next_sibling:
                end_node = end_node.next_sibling
                logging.debug("Moving to next sibling")
            elif end_node.parent:
                end_node = end_node.parent
                logging.debug("Moving to parent")
            else:
                logging.warning("Reached end of tree without finding balanced statement")
                break

            depth += 1

        if depth == max_depth:
            logging.warning(f"Max depth ({max_depth}) reached while capturing console.log: {full_statement}")

        full_statement = full_statement.strip()
        if not full_statement.endswith(';'):
            full_statement += ';'
            logging.debug("Added missing semicolon to statement")

        # Ensure the final statement doesn't exceed the chunk size
        if len(full_statement) > self._chunk_size:
            full_statement = full_statement[:self._chunk_size]
            logging.warning(f"Truncated console.log statement to fit chunk size: {full_statement}")

        logging.debug(f"Final captured console.log statement (depth {depth}): {full_statement}")
        return full_statement

    def _add_chunk(self, chunk: str, chunks: List[str]) -> None:
        logging.debug(f"Attempting to add chunk: {chunk[:100]}...")  # Log first 100 chars
        if len(chunks) >= self._top_k:
            logging.debug(f"Skipping chunk addition: already have {len(chunks)} chunks (top_k: {self._top_k})")
            return

        # Ensure chunk size doesn't exceed the limit
        if len(chunk) > self._chunk_size:
            logging.debug(f"Chunk exceeds size limit. Splitting chunk of size {len(chunk)}")
            self._split_and_add(chunk, chunks)
            return

        # Prioritize keeping console.log statements intact
        if self._is_console_log(chunk):
            if len(chunks) < self._top_k:
                chunks.append(chunk)
                logging.debug(f"Added console log chunk directly. Size: {len(chunk)}")
            elif len(chunk) > len(chunks[-1]):
                chunks[-1] = chunk
                logging.debug(f"Replaced last chunk with longer console log. Size: {len(chunk)}")
        else:
            # For non-console.log chunks
            if len(chunks) < self._top_k:
                chunks.append(chunk)
                logging.debug(f"Added non-console.log chunk directly. Size: {len(chunk)}")
            elif len(chunk) > len(chunks[-1]):
                chunks[-1] = chunk
                logging.debug(f"Replaced last chunk with longer non-console.log chunk. Size: {len(chunk)}")

        # Ensure we don't exceed top_k chunks
        chunks[:] = chunks[:self._top_k]

        # Sort chunks by length in descending order, prioritizing console.log statements
        chunks.sort(key=lambda x: (not self._is_console_log(x), -len(x)))
        logging.debug(f"After adding chunk, total chunks: {len(chunks)}")
        logging.debug(f"Current chunks: {[chunk[:50] + '...' for chunk in chunks]}")  # Log first 50 chars of each chunk
        logging.debug(f"Chunk lengths: {[len(chunk) for chunk in chunks]}")

    def _split_and_add(self, chunk: str, chunks: List[str]) -> None:
        lines = chunk.split('\n')
        current_chunk = ""
        for line in lines:
            if len(current_chunk) + len(line) + 1 <= self._chunk_size:
                current_chunk += line + "\n"
            else:
                if current_chunk:
                    self._add_split_chunk(current_chunk.strip(), chunks)
                    if len(chunks) >= self._top_k:
                        return
                current_chunk = line[:self._chunk_size] + "\n"

            while len(current_chunk) > self._chunk_size:
                self._add_split_chunk(current_chunk[:self._chunk_size].strip(), chunks)
                if len(chunks) >= self._top_k:
                    return
                current_chunk = current_chunk[self._chunk_size:]

        if current_chunk:
            self._add_split_chunk(current_chunk.strip(), chunks)

    def _add_split_chunk(self, chunk: str, chunks: List[str]) -> None:
        if len(chunk) > self._chunk_size:
            # Split the chunk if it's larger than the maximum size
            for i in range(0, len(chunk), self._chunk_size):
                sub_chunk = chunk[i:i+self._chunk_size]
                truncated_sub_chunk = sub_chunk[:self._chunk_size]  # Ensure sub_chunk doesn't exceed chunk_size
                if len(chunks) < self._top_k:
                    chunks.append(truncated_sub_chunk)
                    logging.debug(f"Added split sub-chunk: {truncated_sub_chunk[:100]}...")  # Log first 100 chars
                elif len(truncated_sub_chunk) > len(chunks[-1]):
                    chunks[-1] = truncated_sub_chunk
                    logging.debug(f"Replaced last chunk with longer split sub-chunk: {truncated_sub_chunk[:100]}...")  # Log first 100 chars
                else:
                    break  # Stop if we've reached top_k and the new sub-chunk isn't longer
        else:
            truncated_chunk = chunk[:self._chunk_size]  # Ensure chunk doesn't exceed chunk_size
            if len(chunks) < self._top_k:
                chunks.append(truncated_chunk)
                logging.debug(f"Added split chunk: {truncated_chunk[:100]}...")  # Log first 100 chars
            elif len(truncated_chunk) > len(chunks[-1]):
                chunks[-1] = truncated_chunk
                logging.debug(f"Replaced last chunk with longer split chunk: {truncated_chunk[:100]}...")  # Log first 100 chars
        logging.debug(f"Current chunk sizes after _add_split_chunk: {[len(c) for c in chunks]}")

    def _default_split(self, text: str) -> List[str]:
        chunks = []
        for i in range(0, len(text), self._chunk_size):
            chunk = text[i:i + self._chunk_size]
            chunks.append(chunk.strip())
        return sorted(chunks, key=len, reverse=True)[:self._top_k]  # Apply top_k limit to longest chunks

    def _is_console_log(self, text: str) -> bool:
        # Check for console.log and its variants, including those with template literals
        log_patterns = [
            r'console\.(?:log|error|warn|info|debug)\s*\(',  # Regular console.log calls
            r'console\.(?:log|error|warn|info|debug)\s*`',  # Console.log with template literals
            r'console\.(?:log|error|warn|info|debug)\s*\(\s*`',  # Console.log with parentheses and template literals
            r'console\.(?:log|error|warn|info|debug)\s*\(\s*`[^`]*\$\{[^}]*\}[^`]*`\s*\)',  # More specific pattern for template literals
            r'console\.(?:log|error|warn|info|debug)\s*\(\s*[`"].*?\$\{.*?\}.*?[`"]\s*\)',  # Pattern for complex template literals
            r'console\.(?:log|error|warn|info|debug)\s*\(\s*[`"](?:[^`"\\]|\\.|\$\{(?:[^{}]|\{[^}]*\})*\})*[`"]\s*\)',  # Nested template literals
            r'console\.(?:log|error|warn|info|debug)\s*\(\s*(?:[^()]+|\([^()]*\))*\s*\)',  # Catch-all pattern for various argument types
            r'console\.(?:log|error|warn|info|debug)\s*\(\s*`(?:[^`\\]|\\.|\$\{(?:[^{}]|\{[^}]*\})*\})*`\s*\)',  # TypeScript-specific template literal pattern
            r'console\.(?:log|error|warn|info|debug)\s*\(\s*(?:[^,]+,\s*)*`(?:[^`\\]|\\.|\$\{(?:[^{}]|\{[^}]*\})*\})*`\s*(?:,\s*[^)]+)*\s*\)'  # Multiple arguments with template literals
        ]
        for i, pattern in enumerate(log_patterns):
            if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                logging.debug(f"Matched console.log pattern {i}: {pattern}")
                logging.debug(f"Matched text: {text[:200]}...")  # Log first 200 chars of matched text
                return True
        logging.debug(f"No console.log pattern matched for text: {text[:200]}...")  # Log first 200 chars of unmatched text
        logging.debug(f"Full unmatched text: {text}")  # Log the full unmatched text for thorough debugging
        return False

    def get_chunk_size(self) -> int:
        return self._chunk_size

    def set_chunk_size(self, size: int) -> None:
        self._chunk_size = size

    def get_top_k(self) -> int:
        return self._top_k

    def set_top_k(self, k: int) -> None:
        self._top_k = k


class CodeEmbedder:
    def __init__(self, persist_directory: str = "./chroma_db", chunk_size: int = 512, top_k: int = 5) -> None:
        self.persist_directory: str = persist_directory
        self._chunk_size: int = chunk_size
        self._top_k: int = top_k
        self.embedding_function: Embeddings = self._initialize_embedding_function()
        self.default_text_splitter: RecursiveCharacterTextSplitter = (
            RecursiveCharacterTextSplitter(
                chunk_size=self._chunk_size,
                chunk_overlap=0,
                length_function=len,
            )
        )
        self.vectorstore: Chroma = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding_function,
        )
        self.extension_to_language: Dict[str, str] = {}
        self._initialize_extension_to_language_map()
        self.text_splitters: Dict[str, TreeSitterTextSplitter] = {}

    def _initialize_embedding_function(self) -> Embeddings:
        if "VOYAGE_API_KEY" in os.environ:
            return VoyageEmbeddings(model="voyage-code-2")
        else:
            return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    def _initialize_extension_to_language_map(self) -> None:
        supported_languages = {
            'python': ['.py', '.pyw'],
            'javascript': ['.js', '.jsx'],
            'typescript': ['.ts', '.tsx'],
            'java': ['.java'],
            'c': ['.c', '.h'],
            'cpp': ['.cpp', '.hpp', '.cc', '.hh'],
            'ruby': ['.rb'],
            'go': ['.go'],
            'rust': ['.rs'],
        }
        for language, extensions in supported_languages.items():
            for ext in extensions:
                self.extension_to_language[ext] = language

    def get_language_from_extension(self, file_path: str) -> Optional[str]:
        _, ext = os.path.splitext(file_path)
        return self.extension_to_language.get(ext)

    def get_text_splitter(self, language: Optional[str], file_extension: str = '') -> RecursiveCharacterTextSplitter:
        if language in self.extension_to_language.values():
            if language not in self.text_splitters:
                try:
                    self.text_splitters[language] = TreeSitterTextSplitter(language, chunk_size=self._chunk_size, top_k=self._top_k)
                except ValueError as e:
                    print(f"Warning: {str(e)}. Falling back to default splitter.")
                    return self.default_text_splitter
            return self.text_splitters[language]
        return self.default_text_splitter

    def init_embeddings(self, file_paths: List[str]) -> None:
        for file_path in file_paths:
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                continue

            language: Optional[str] = self.get_language_from_extension(file_path)
            text_splitter: RecursiveCharacterTextSplitter = self.get_text_splitter(language)

            try:
                loader: TextLoader = TextLoader(file_path)
                documents: List[Document] = loader.load()

                for doc in documents:
                    doc.metadata["language"] = language
                    doc.metadata["file_path"] = file_path

                chunks: List[Document] = text_splitter.split_documents(documents)

                self.vectorstore.add_documents(chunks)

                print(f"Added embeddings for file: {file_path} (Language: {language})")

            except Exception as e:
                print(f"Error processing file {file_path}: {str(e)}")

        self.vectorstore.persist()

    def lookup_similar_chunks(
        self, query: str, top_k: Optional[int] = None, language: Optional[str] = None
    ) -> List[Dict[str, str | float]]:
        filter_dict: Optional[Dict[str, str]] = (
            {"language": language} if language else None
        )

        k = top_k if top_k is not None else self._top_k

        results: List[Tuple[Document, float]] = (
            self.vectorstore.similarity_search_with_score(
                query, k=k, filter=filter_dict
            )
        )

        return [
            {
                "chunk": doc.page_content,
                "score": score,
                "language": doc.metadata["language"],
                "file_path": doc.metadata["file_path"],
            }
            for doc, score in results
        ]

    def get_chunk_size(self) -> int:
        return self._chunk_size

    def set_chunk_size(self, size: int) -> None:
        self._chunk_size = size
        for splitter in self.text_splitters.values():
            splitter.set_chunk_size(size)

    def get_top_k(self) -> int:
        return self._top_k

    def set_top_k(self, k: int) -> None:
        self._top_k = k
        for splitter in self.text_splitters.values():
            splitter.set_top_k(k)


# Example usage:
# embedder: CodeEmbedder = CodeEmbedder()
# file_paths: List[str] = ["example.py", "example.js", "example.java"]
# embedder.init_embeddings(file_paths)
#
# query: str = "How to implement a binary search?"
# similar_chunks: List[Dict[str, str | float]] = embedder.lookup_similar_chunks(query)
# for chunk in similar_chunks:
#     print(f"Language: {chunk['language']}")
#     print(f"File: {chunk['file_path']}")
#     print(f"Similarity: {chunk['score']}")
#     print(f"Chunk: {chunk['chunk']}\n")
