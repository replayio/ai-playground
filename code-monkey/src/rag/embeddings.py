import os
from typing import List, Dict, Optional, Tuple, Union
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings, VoyageEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.schema import Document


class CodeEmbedder:
    def __init__(self, persist_directory: str = "./chroma_db") -> None:
        self.persist_directory: str = persist_directory
        self.embedding_function: Embeddings = self._initialize_embedding_function()
        self.text_splitter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.vectorstore: Chroma = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding_function,
        )

    def _initialize_embedding_function(self) -> Embeddings:
        if "VOYAGE_API_KEY" in os.environ:
            return VoyageEmbeddings(model="voyage-code-2")
        else:
            return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    def add_documents(self, file_paths: List[str]) -> None:
        for file_path in file_paths:
            if not os.path.exists(file_path):
                continue

            loader: TextLoader = TextLoader(file_path)
            documents: List[Document] = loader.load()

            for doc in documents:
                doc.metadata["file_path"] = file_path

            chunks: List[Document] = self.text_splitter.split_documents(documents)
            self.vectorstore.add_documents(chunks)

        self.vectorstore.persist()

    def query(self, query: str, k: int = 4) -> List[Dict[str, Union[str, float]]]:
        results: List[Tuple[Document, float]] = self.vectorstore.similarity_search_with_score(query, k=k)

        return [
            {
                "chunk": doc.page_content,
                "score": score,
                "file_path": doc.metadata["file_path"],
            }
            for doc, score in results
        ]
