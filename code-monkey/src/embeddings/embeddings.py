import os
import fnmatch
from abc import ABC, abstractmethod
import voyageai

# Assuming voyageai is already installed and available for import
# Assuming the existence of a function tokenize_for_embedding that partially tokenizes the content

class Embeddings(ABC):
    def read_files(self, folder):
        def is_ignored(path, ignore_patterns):
            return any(fnmatch.fnmatch(path, pattern) for pattern in ignore_patterns)

        ignore_file = os.path.join(folder, '.gitignore')
        ignore_patterns = []
        if os.path.exists(ignore_file):
            with open(ignore_file, 'r') as f:
                ignore_patterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        all_files = []
        for root, dirs, files in os.walk(folder):
            dirs[:] = [d for d in dirs if not is_ignored(os.path.join(root, d), ignore_patterns)]
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
        self.embed()

    def embed(self):
        files = self.read_files(self.folder)
        for file in files:
            with open(file, 'r') as f:
                content = f.read()
                # Chunking the file content for partial processing
                chunks = self.chunk_content(content)
                embeddings = []
                for chunk in chunks:
                    # Partial tokenization of the chunk
                    partial_tokens = tokenize_for_embedding(chunk)
                    # Use the Voyage AI API to create embeddings for each chunk
                    client = voyageai.Client()
                    chunk_embedding = client.embed(partial_tokens)
                    embeddings.append(chunk_embedding)
                # Store the combined embeddings for the file
                self.embeddings[file] = embeddings

    def chunk_content(self, content, chunk_size=512):
        # Split the content into chunks of specified size
        return [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]

    def run_prompt(self, prompt: str):
        # Here you would implement the logic to run the prompt on the stored embeddings
        # using the Voyage AI API. For now, we'll just return a placeholder response.
        return f"Running prompt '{prompt}' on Voyage embeddings (not implemented)"
