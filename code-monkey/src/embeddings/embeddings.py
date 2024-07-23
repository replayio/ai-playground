import os
import fnmatch
import requests
import numpy as np
from scipy.spatial.distance import cosine
from abc import ABC, abstractmethod

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
        api_key = os.environ.get('VOYAGE_API_KEY')
        if not api_key:
            raise ValueError("VOYAGE_API_KEY environment variable is not set")

        files = self.read_files(self.folder)
        for file in files:
            with open(file, 'r') as f:
                content = f.read()
                # Use the Voyage AI API to create embeddings
                response = requests.post(
                    'https://api.voyageai.com/v1/models/voyage-code-2/embeddings',
                    headers={'Authorization': f"Bearer {api_key}"},
                    json={'text': content}
                )
                if response.status_code == 200:
                    self.embeddings[file] = response.json()
                else:
                    raise Exception(f"Failed to get embeddings for {file}, status code: {response.status_code}")

    def run_prompt(self, prompt: str):
        api_key = os.environ.get('VOYAGE_API_KEY')
        if not api_key:
            raise ValueError("VOYAGE_API_KEY environment variable is not set")

        # Get embedding for the prompt
        response = requests.post(
            'https://api.voyageai.com/v1/models/voyage-code-2/embeddings',
            headers={'Authorization': f"Bearer {api_key}"},
            json={'text': prompt}
        )
        if response.status_code != 200:
            raise Exception(f"Failed to get embedding for prompt, status code: {response.status_code}")

        prompt_embedding = np.array(response.json()['embeddings'][0])

        # Find the most similar file
        max_similarity = -1
        most_similar_file = None

        for file, embedding_data in self.embeddings.items():
            file_embedding = np.array(embedding_data['embeddings'][0])
            similarity = 1 - cosine(prompt_embedding, file_embedding)
            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_file = file

        if most_similar_file:
            with open(most_similar_file, 'r') as f:
                return f.read()
        else:
            return "No matching file found"
