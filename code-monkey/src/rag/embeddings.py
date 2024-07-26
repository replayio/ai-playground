import os
from typing import List, Dict, Optional, Tuple
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.embeddings import VoyageEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from tree_sitter import Parser, Language, Tree, Node

CHUNK_LENGTH: int = 512

SUPPORTED_LANGUAGES: Dict[str, List[str]] = {
    "python": [".py", ".pyw"],
    "javascript": [".js", ".jsx", ".ts", ".tsx"],
    "java": [".java"],
    "c": [".c", ".h"],
    "cpp": [".cpp", ".hpp", ".cc", ".hh"],
    "ruby": [".rb"],
    "go": [".go"],
    "rust": [".rs"],
}


class TreeSitterTextSplitter(RecursiveCharacterTextSplitter):
    def __init__(self, language: str) -> None:
        lib_path: str = os.path.join("build", f"{language}.so")
        lang: Language = Language(lib_path, language)
        self.language: str = language
        self.parser: Parser = Parser(lang)

        super().__init__(chunk_size=CHUNK_LENGTH, chunk_overlap=0)

    def split_text(self, text: str) -> List[str]:
        tree: Tree = self.parser.parse(bytes(text, "utf8"))

        chunks: List[str] = []

        def traverse_tree(node: Node, start: int = 0) -> int:
            if node.end_byte - start >= CHUNK_LENGTH:
                chunks.append(text[start : node.end_byte])
                start = node.end_byte

            for child in node.children:
                start = traverse_tree(child, start)

            return start

        traverse_tree(tree.root_node)
        return chunks


class CodeEmbedder:
    def __init__(self, persist_directory: str = "./chroma_db") -> None:
        self.persist_directory: str = persist_directory
        self.embedding_function: Embeddings = self._initialize_embedding_function()
        self.default_text_splitter: RecursiveCharacterTextSplitter = (
            RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_LENGTH,
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

    def _initialize_embedding_function(self) -> Embeddings:
        if "VOYAGE_API_KEY" in os.environ:
            return VoyageEmbeddings(model="voyage-code-2")
        else:
            return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    def _initialize_extension_to_language_map(self) -> None:
        for language, extensions in SUPPORTED_LANGUAGES.items():
            for ext in extensions:
                self.extension_to_language[ext] = language

    def get_language_from_extension(self, file_path: str) -> Optional[str]:
        _, ext = os.path.splitext(file_path)
        return self.extension_to_language.get(ext)

    def get_text_splitter(
        self, language: Optional[str]
    ) -> RecursiveCharacterTextSplitter:
        if language in SUPPORTED_LANGUAGES:
            try:
                return TreeSitterTextSplitter(language)
            except ValueError as e:
                print(f"Warning: {str(e)}. Falling back to default splitter.")
        return self.default_text_splitter

    def init_embeddings(self, file_paths: List[str]) -> None:
        for file_path in file_paths:
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                continue

            language: Optional[str] = self.get_language_from_extension(file_path)
            text_splitter: RecursiveCharacterTextSplitter = self.get_text_splitter(
                language
            )

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
        self, query: str, top_k: int = 5, language: Optional[str] = None
    ) -> List[Dict[str, str | float]]:
        filter_dict: Optional[Dict[str, str]] = (
            {"language": language} if language else None
        )

        results: List[Tuple[Document, float]] = (
            self.vectorstore.similarity_search_with_score(
                query, k=top_k, filter=filter_dict
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
