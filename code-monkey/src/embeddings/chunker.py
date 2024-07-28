import os
from tree_sitter import Language, Parser

# Load tree-sitter languages
PY_LANGUAGE = Language("build/my-languages.so", "python")
JS_LANGUAGE = Language("build/my-languages.so", "javascript")
JAVA_LANGUAGE = Language("build/my-languages.so", "java")
CPP_LANGUAGE = Language("build/my-languages.so", "cpp")


class Chunk:
    def __init__(self, content, file_path, start_line, end_line):
        self.content = content
        self.file_path = file_path
        self.start_line = start_line
        self.end_line = end_line

    def __str__(self):
        return f"Chunk from {self.file_path} (lines {self.start_line}-{self.end_line}):\n{self.content}"


class Chunker:
    def __init__(self, max_chunk_size=512):
        self.max_chunk_size = max_chunk_size

    def chunk_content(self, content, file_path):
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == ".py":
            language = PY_LANGUAGE
        elif file_extension in (".js", ".jsx"):
            language = JS_LANGUAGE
        elif file_extension == ".java":
            language = JAVA_LANGUAGE
        elif file_extension in (".cpp", ".hpp", ".c", ".h"):
            language = CPP_LANGUAGE
        else:
            # Fallback to simple chunking for unsupported languages
            return self._simple_chunk(content, file_path)

        parser = Parser()
        parser.set_language(language)
        tree = parser.parse(bytes(content, "utf8"))

        return self._traverse_tree(tree.root_node, content, file_path)

    def _simple_chunk(self, content, file_path):
        chunks = []
        lines = content.split("\n")
        current_chunk = ""
        start_line = 1

        for i, line in enumerate(lines, 1):
            if len(current_chunk) + len(line) > self.max_chunk_size:
                if current_chunk:
                    chunks.append(Chunk(current_chunk, file_path, start_line, i - 1))
                current_chunk = line + "\n"
                start_line = i
            else:
                current_chunk += line + "\n"

        if current_chunk:
            chunks.append(Chunk(current_chunk, file_path, start_line, len(lines)))

        return chunks

    def _traverse_tree(self, node, content, file_path):
        chunks = []
        node_content = content[node.start_byte : node.end_byte]
        start_line = content.count("\n", 0, node.start_byte) + 1
        end_line = content.count("\n", 0, node.end_byte) + 1

        if len(node_content) <= self.max_chunk_size:
            chunks.append(Chunk(node_content, file_path, start_line, end_line))
        else:
            # Summarize the node if it exceeds the chunk size
            summary = self._summarize_node(node, content)
            if len(summary) <= self.max_chunk_size:
                chunks.append(Chunk(summary, file_path, start_line, end_line))
            else:
                # Split the summary into multiple chunks if it's still too large
                sub_chunks = self._simple_chunk(summary, file_path)
                chunks.extend(sub_chunks)

        for child in node.children:
            chunks.extend(self._traverse_tree(child, content, file_path))

        return chunks

    def _summarize_node(self, node, content):
        node_type = node.type

        # Create a summary based on the node type
        if node_type in ("function_definition", "class_definition"):
            # Extract function or class name
            name_node = node.child_by_field_name("name")
            name = (
                content[name_node.start_byte : name_node.end_byte]
                if name_node
                else "Unknown"
            )

            # Extract parameters for functions
            params = ""
            if node_type == "function_definition":
                params_node = node.child_by_field_name("parameters")
                if params_node:
                    params = content[params_node.start_byte : params_node.end_byte]

            # Create a summary
            summary = f"{node_type.replace('_', ' ').title()}: {name}{params}\n"

            # Add a brief description of the body
            body_node = node.child_by_field_name("body")
            if body_node:
                summary += "Body structure:\n"
                for child in body_node.children:
                    summary += f"- {child.type}\n"
        else:
            # For other node types, create a brief summary of the structure
            summary = f"{node_type.replace('_', ' ').title()}:\n"
            for child in node.children:
                summary += f"- {child.type}\n"

        return summary
