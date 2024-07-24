import os
import fnmatch
from abc import ABC, abstractmethod
import voyageai
import anthropic
from scipy.spatial.distance import cosine
from tree_sitter import Language, Parser
import re

# Load tree-sitter languages
PY_LANGUAGE = Language('build/my-languages.so', 'python')
JS_LANGUAGE = Language('build/my-languages.so', 'javascript')
JAVA_LANGUAGE = Language('build/my-languages.so', 'java')
CPP_LANGUAGE = Language('build/my-languages.so', 'cpp')

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
        self.anthropic_client = anthropic.Anthropic()
        self.voyage_client = voyageai.Client()

    def embed(self):
        files = self.read_files(self.folder)
        for file in files:
            with open(file, 'r') as f:
                content = f.read()
                # Chunking the file content using tree-sitter
                chunks = self.chunk_content(content, file)
                embeddings = []
                for chunk in chunks:
                    # Use the Voyage AI API to create embeddings for each chunk
                    chunk_embedding = self.voyage_client.embed(chunk)
                    embeddings.append(chunk_embedding)
                # Store the combined embeddings for the file
                self.embeddings[file] = embeddings

    def chunk_content(self, content, file_path, max_chunk_size=512):
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.py':
            language = PY_LANGUAGE
        elif file_extension in ('.js', '.jsx'):
            language = JS_LANGUAGE
        elif file_extension == '.java':
            language = JAVA_LANGUAGE
        elif file_extension in ('.cpp', '.hpp', '.c', '.h'):
            language = CPP_LANGUAGE
        else:
            # Fallback to simple chunking for unsupported languages
            return [content[i:i+max_chunk_size] for i in range(0, len(content), max_chunk_size)]

        parser = Parser()
        parser.set_language(language)
        tree = parser.parse(bytes(content, "utf8"))

        def traverse_tree(node, depth=0):
            chunks = []
            node_content = content[node.start_byte:node.end_byte]
            
            if len(node_content) <= max_chunk_size:
                chunks.append(node_content)
            else:
                # Summarize the node if it exceeds the chunk size
                summary = self.summarize_node(node, content)
                if len(summary) <= max_chunk_size:
                    chunks.append(summary)
                else:
                    # Split the summary into multiple chunks if it's still too large
                    chunks.extend([summary[i:i+max_chunk_size] for i in range(0, len(summary), max_chunk_size)])

            for child in node.children:
                chunks.extend(traverse_tree(child, depth + 1))

            return chunks

        return traverse_tree(tree.root_node)

    def summarize_node(self, node, content):
        node_content = content[node.start_byte:node.end_byte]
        node_type = node.type
        
        # Create a summary based on the node type
        if node_type in ('function_definition', 'class_definition'):
            # Extract function or class name
            name_node = node.child_by_field_name('name')
            name = content[name_node.start_byte:name_node.end_byte] if name_node else 'Unknown'
            
            # Extract parameters for functions
            params = ''
            if node_type == 'function_definition':
                params_node = node.child_by_field_name('parameters')
                if params_node:
                    params = content[params_node.start_byte:params_node.end_byte]
            
            # Create a summary
            summary = f"{node_type.replace('_', ' ').title()}: {name}{params}\n"
            
            # Add a brief description of the body
            body_node = node.child_by_field_name('body')
            if body_node:
                body_content = content[body_node.start_byte:body_node.end_byte]
                body_lines = body_content.split('\n')
                summary += f"Body: {len(body_lines)} lines\n"
                if len(body_lines) > 2:
                    summary += f"First line: {body_lines[0].strip()}\n"
                    summary += f"Last line: {body_lines[-1].strip()}\n"
        else:
            # For other node types, create a brief summary
            lines = node_content.split('\n')
            summary = f"{node_type.replace('_', ' ').title()}:\n"
            summary += f"Content: {len(lines)} lines\n"
            if len(lines) > 2:
                summary += f"First line: {lines[0].strip()}\n"
                summary += f"Last line: {lines[-1].strip()}\n"
        
        return summary

    def get_most_similar_chunks(self, prompt, top_k=3):
        prompt_embedding = self.voyage_client.embed(prompt)
        similarities = []
        for file, chunks in self.embeddings.items():
            for i, chunk_embedding in enumerate(chunks):
                similarity = 1 - cosine(prompt_embedding, chunk_embedding)
                similarities.append((file, i, similarity))
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
        for file, chunk_index, _ in similar_chunks:
            with open(file, 'r') as f:
                content = f.read()
                chunks = self.chunk_content(content)
                context += f"File: {file}\nChunk {chunk_index}:\n{chunks[chunk_index]}\n\n"

        return self.generate_response(prompt, context)

# Example usage
# embeddings = VoyageEmbeddings("/path/to/code/folder")
# response = embeddings.run_prompt("Explain the main function in the code.")
# print(response)
