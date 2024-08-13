import os
import fnmatch
from abc import ABC, abstractmethod
import voyageai
import anthropic
from scipy.spatial.distance import cosine
from chunker import Chunker


class Embeddings(ABC):
    def read_files(self, folder):
        def is_ignored(path, ignore_patterns):
            return any(fnmatch.fnmatch(path, pattern) for pattern in ignore_patterns)

        ignore_file = os.path.join(folder, ".gitignore")
        ignore_patterns = []
        if os.path.exists(ignore_file):
            with open(ignore_file, "r") as f:
                ignore_patterns = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]

        all_files = []
        for root, dirs, files in os.walk(folder):
            dirs[:] = [
                d
                for d in dirs
                if not is_ignored(os.path.join(root, d), ignore_patterns)
            ]
            for file in files:
                file_path = os.path.join(root, file)
                if not is_ignored(file_path, ignore_patterns):
                    all_files.append(file_path)

        return all_files

    @abstractmethod
    def run_prompt(self, prompt: str):
        pass


class VoyageEmbeddings(Embeddings):
    def __init__(self, folder):
        self.folder = folder
        self.embeddings = {}
        self.chunker = Chunker()
        self.embed()
        self.anthropic_client = anthropic.Anthropic()
        self.voyage_client = voyageai.Client()

    def embed(self):
        files = self.read_files(self.folder)
        for file in files:
            with open(file, "r") as f:
                content = f.read()
                # Chunking the file content using the Chunker class
                chunks = self.chunker.chunk_content(content, file)
                embeddings = []
                for chunk in chunks:
                    # Use the Voyage AI API to create embeddings for each chunk
                    chunk_embedding = self.voyage_client.embed(chunk.content)
                    embeddings.append((chunk, chunk_embedding))
                # Store the combined embeddings for the file
                self.embeddings[file] = embeddings

    def get_most_similar_chunks(self, prompt, top_k=3):
        prompt_embedding = self.voyage_client.embed(prompt)
        similarities = []
        for file, chunks in self.embeddings.items():
            for chunk, chunk_embedding in chunks:
                similarity = 1 - cosine(prompt_embedding, chunk_embedding)
                similarities.append((file, chunk, similarity))
        return sorted(similarities, key=lambda x: x[2], reverse=True)[:top_k]

    def generate_response(self, prompt, context):
        messages = [
            {"role": "human", "content": f"Context:\n{context}\n\nQuestion: {prompt}"}
        ]
        response = self.anthropic_client.messages.create(
            model="claude-3-opus-20240229",
            messages=messages,
            max_tokens=1000,
        )
        return response.content

    def run_prompt(self, prompt: str):
        similar_chunks = self.get_most_similar_chunks(prompt)
        context = ""
        for file, chunk, _ in similar_chunks:
            context += f"File: {file}\n{str(chunk)}\n\n"

        return self.generate_response(prompt, context)


# Example usage
# embeddings = VoyageEmbeddings("/path/to/code/folder")
# chunks = embeddings.get_most_similar_chunks("Explain the main function in the code.")
# TODO: Stringify the chunks.
# print(response)
