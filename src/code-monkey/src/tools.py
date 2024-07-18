import os
import shutil
import traceback
from enum import Enum
from typing import List, Dict, Set, Any
import subprocess
from deps import DependencyGraph


class AgentName(Enum):
    Openai = 1
    Claude = 2


src_dir = os.path.dirname(os.path.abspath(__file__))
artifacts_dir = os.path.join(src_dir, "..", "artifacts")


def make_file_path(name: str) -> str:
    file_path = os.path.join(artifacts_dir, name)
    if os.path.commonpath([file_path, artifacts_dir]) != artifacts_dir:
        raise ValueError("Access to file outside artifacts directory is not allowed")
    return file_path


# Helper functions
def ask_user(prompt: str) -> str:
    print(prompt)
    return input()


def get_file_tree(directory: str) -> Set[str]:
    relative_paths = set()
    for root, dirs, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, directory)
            relative_paths.add(relative_path)
    return relative_paths


def copy_src() -> List[str]:
    dest_dir = artifacts_dir

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    try:
        shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)
    except Exception as e:
        print(f"Directory not copied. Error: {str(e)}")

    return list(get_file_tree(dest_dir))


class Tool:
    name: str
    description: str
    input_schema: Dict[str, Any]

    @classmethod
    def handle_tool_call(self, input: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement handle_tool_call method")


class IOTool(Tool):
    modified_files: Set[str] = set()

    @classmethod
    def track_modified_file(self, file_path: str):
        self.modified_files.add(os.path.relpath(file_path, artifacts_dir))

    @classmethod
    def clear_modified_files(self):
        self.modified_files.clear()


class GetDependenciesTool(Tool):
    name = "get_dependencies"
    description = "Get the dependency graph for one or more Python modules"
    input_schema = {
        "type": "object",
        "properties": {
            "module_names": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of module names to get dependencies for",
            },
        },
        "required": ["module_names"],
    }

    @classmethod
    def handle_tool_call(self, input: Dict[str, Any]) -> Dict[str, Any]:
        module_names = input["module_names"]
        module_paths = [
            os.path.join(artifacts_dir, f"{module}.py") for module in module_names
        ]
        dependency_graph = DependencyGraph(module_paths)
        dependencies = {
            module.name: [dep.name for dep in module.dependencies]
            for module in dependency_graph.modules.values()
        }
        return {"dependencies": dependencies}


class ReadFileTool(IOTool):
    name = "read_file"
    description = "Read the contents of the file of given name"
    input_schema = {
        "type": "object",
        "properties": {
            "fname": {"type": "string"},
        },
        "required": ["fname"],
    }

    @classmethod
    def handle_tool_call(self, input: Dict[str, Any]) -> Dict[str, Any]:
        name = input["fname"]
        file_path = make_file_path(name)
        with open(file_path, "r") as file:
            content = file.read()
        self.track_modified_file(file_path)
        return {"content": content}


class WriteFileTool(IOTool):
    name = "write_file"
    description = "Write content to the file of given name"
    input_schema = {
        "type": "object",
        "properties": {
            "fname": {"type": "string", "description": "Name of the file to edit."},
            "content": {
                "type": "string",
                "description": "New contents of the file.",
            },
        },
        "required": ["fname", "content"],
    }

    @classmethod
    def handle_tool_call(self, input: Dict[str, Any]) -> Dict[str, Any]:
        name = input["fname"]
        content = input["content"]
        file_path = make_file_path(name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as file:
            file.write(content)
        self.track_modified_file(file_path)
        return {}


class AskUserTool(Tool):
    name = "ask_user"
    description = "Ask the user a question and return their response"
    input_schema = {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "The prompt to show the user",
            }
        },
        "required": ["prompt"],
    }

    @classmethod
    def handle_tool_call(self, input: Dict[str, Any]) -> Dict[str, Any]:
        prompt = input["prompt"]
        print(prompt)
        response = input()
        return {"content": response}


class ReplaceInFileTool(IOTool):
    name = "replace_in_file"
    description = "Replace a specific string in a file with another string"
    input_schema = {
        "type": "object",
        "properties": {
            "fname": {"type": "string", "description": "Name of the file to edit."},
            "to_replace": {
                "type": "string",
                "description": "The string to be replaced.",
            },
            "replacement": {
                "type": "string",
                "description": "The string to replace with.",
            },
        },
        "required": ["fname", "to_replace", "replacement"],
    }

    @classmethod
    def handle_tool_call(self, input: Dict[str, Any]) -> Dict[str, Any]:
        name = input["fname"]
        to_replace = input["to_replace"]
        replacement = input["replacement"]
        file_path = make_file_path(name)
        with open(file_path, "r") as file:
            content = file.read()

        occurrences = content.count(to_replace)
        if occurrences != 1:
            raise Exception(
                f"The string '{to_replace}' appears {occurrences} times in the file. It must appear exactly once for replacement."
            )

        new_content = content.replace(to_replace, replacement)

        with open(file_path, "w") as file:
            file.write(new_content)

        self.track_modified_file(file_path)
        return {
            "message": f"Replacement successful. '{to_replace}' was replaced with '{replacement}'.",
        }


class RenameFileTool(IOTool):
    name = "rename_file"
    description = "Rename a file"
    input_schema = {
        "type": "object",
        "properties": {
            "old_name": {
                "type": "string",
                "description": "Current name of the file.",
            },
            "new_name": {"type": "string", "description": "New name for the file."},
        },
        "required": ["old_name", "new_name"],
    }

    @classmethod
    def handle_tool_call(self, input: Dict[str, Any]) -> Dict[str, Any]:
        old_name = input["old_name"]
        new_name = input["new_name"]
        old_path = make_file_path(old_name)
        new_path = make_file_path(new_name)

        if not os.path.exists(old_path):
            raise FileNotFoundError(f"The file {old_name} does not exist.")

        new_dir = os.path.dirname(new_path)
        os.makedirs(new_dir, exist_ok=True)

        if os.path.exists(new_path):
            raise FileExistsError(f"The file {new_name} already exists.")

        os.rename(old_path, new_path)
        self.track_modified_file(old_path)
        self.track_modified_file(new_path)
        return {}


class DeleteFileTool(IOTool):
    name = "delete_file"
    description = "Delete a file"
    input_schema = {
        "type": "object",
        "properties": {
            "fname": {
                "type": "string",
                "description": "Name of the file to delete.",
            },
        },
        "required": ["fname"],
    }

    @classmethod
    def handle_tool_call(self, input: Dict[str, Any]) -> Dict[str, Any]:
        name = input["fname"]
        file_path = make_file_path(name)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {name} does not exist.")

        os.remove(file_path)
        self.track_modified_file(file_path)
        return {}


class CreateFileTool(IOTool):
    name = "create_file"
    description = "Create a new file with optional content"
    input_schema = {
        "type": "object",
        "properties": {
            "fname": {
                "type": "string",
                "description": "Name of the file to create.",
            },
            "content": {
                "type": "string",
                "description": "Initial content of the file (optional).",
            },
        },
        "required": ["fname"],
    }

    @classmethod
    def handle_tool_call(self, input: Dict[str, Any]) -> Dict[str, Any]:
        name = input["fname"]
        content = input.get("content", "")
        file_path = make_file_path(name)

        if os.path.exists(file_path):
            raise FileExistsError(f"The file {name} already exists.")

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as file:
            file.write(content)

        self.track_modified_file(file_path)
        return {}


class RunTestTool(Tool):
    name = "run_test"
    description = "Run Python tests in a given file and return the results"
    input_schema = {
        "type": "object",
        "properties": {
            "fname": {
                "type": "string",
                "description": "Name of the test file to run.",
            },
        },
        "required": ["fname"],
    }

    @classmethod
    def handle_tool_call(self, input: Dict[str, Any]) -> Dict[str, Any]:
        name = input["fname"]
        file_path = make_file_path(name)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {name} does not exist.")

        result = subprocess.run(
            ["python", "-m", "unittest", file_path],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(file_path),
        )
        return {
            "returncode": str(result.returncode),
            "stdout": result.stdout,
            "stderr": result.stderr,
        }


class RgTool(Tool):
    name = "rg"
    description = (
        "Search for a pattern in files within the artifacts folder using ripgrep"
    )
    input_schema = {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "The pattern to search for.",
            },
        },
        "required": ["pattern"],
    }

    @classmethod
    def handle_tool_call(self, input: Dict[str, Any]) -> Dict[str, Any]:
        pattern = input["pattern"]
        try:
            result = subprocess.run(
                ["rg", "-i", pattern, artifacts_dir],
                capture_output=True,
                text=True,
                check=True,
            )
            return {"content": result.stdout}
        except subprocess.CalledProcessError as e:
            if e.returncode == 1:  # No matches
                return {"content": "No matches found."}
            else:
                raise Exception(f"Error occurred: {e.stderr}")


# Set to store approved commands
approved_commands = set()


class ExecTool(Tool):
    name = "exec"
    description = "Execute a command in the terminal"
    input_schema = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "The command to execute."},
        },
        "required": ["command"],
    }

    @classmethod
    def handle_tool_call(self, input: Dict[str, Any]) -> Dict[str, Any]:
        command = input["command"]
        file_tree = get_file_tree(artifacts_dir)

        # Convert matching file names to absolute paths
        command_parts = command.split()
        for i, part in enumerate(command_parts):
            if part in file_tree:
                command_parts[i] = os.path.join(artifacts_dir, part)

        modified_command = " ".join(command_parts)

        if modified_command not in approved_commands:
            confirmation = ask_user(
                f"Do you want to execute the following command? [Y/n]\n{modified_command}"
            )
            if confirmation.lower() != "y" and confirmation != "":
                raise Exception("Command execution cancelled by user.")
            approved_commands.add(modified_command)

        try:
            result = subprocess.run(
                modified_command, shell=True, capture_output=True, text=True, check=True
            )
            return {"stdout": result.stdout, "stderr": result.stderr}
        except subprocess.CalledProcessError as e:
            error_message = (
                f"Command execution failed with return code {e.returncode}.\n"
            )
            error_message += f"Command: {modified_command}\n"
            error_message += f"Stdout: {e.stdout}\n"
            error_message += f"Stderr: {e.stderr}"
            raise Exception(error_message)


# Updated claude_tools list
claude_tools = [
    GetDependenciesTool,
    ReadFileTool,
    WriteFileTool,
    AskUserTool,
    ReplaceInFileTool,
    RenameFileTool,
    DeleteFileTool,
    CreateFileTool,
    RunTestTool,
    RgTool,
    ExecTool,
]


def handle_claude_tool_call(
    agent: AgentName,
    id: any,
    function_name: str,
    input: Dict[str, Any],
    modified_files: Set[str],
) -> List[Dict[str, Any]]:
    result = {"type": "tool_result", "tool_use_id": id}
    try:
        tool_class = next(
            (tool for tool in claude_tools if tool.name == function_name), None
        )
        if tool_class is None:
            raise Exception(f"Unknown function: {function_name}")

        call_result = tool_class.handle_tool_call(input)
        result["content"] = call_result

        # Add modified files to the parameter
        if issubclass(tool_class, IOTool):
            modified_files.update(tool_class.modified_files)
            tool_class.clear_modified_files()

    except Exception as err:
        print(f"TOOL CALL ERROR: {traceback.format_exc()}")
        result["is_error"] = True
        result["content"] = str(err)
    return result
