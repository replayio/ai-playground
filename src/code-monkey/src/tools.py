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


def make_file_path(name: str, agent: AgentName) -> str:
    file_path = os.path.join(
        # artifacts_dir,  f"{name}_{agent.name.lower()}.txt"
        artifacts_dir,
        name,
    )
    if os.path.commonpath([file_path, artifacts_dir]) != artifacts_dir:
        raise ValueError("Access to file outside artifacts directory is not allowed")
    return file_path


def read_file(name: str, agent: AgentName) -> str:
    file_path = make_file_path(name, agent)
    with open(file_path, "r") as file:
        return file.read()


def write_file(
    name: str,
    agent: AgentName,
    content: str,
) -> str:
    file_path = make_file_path(name, agent)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # # Check for trailing whitespace
    # lines = content.split("\n")
    # i = 1
    # for line in lines:
    #     if line.rstrip() != line:
    #         raise ValueError(
    #             f"Edit rejected. Line {i} must NOT have trailing whitespace: " + line
    #         )
    #     i += 1

    with open(file_path, "w") as file:
        file.write(content)


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


def replace_in_file(
    name: str, agent: AgentName, to_replace: str, replacement: str
) -> str:
    file_path = make_file_path(name, agent)
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

    return f"Replacement successful. '{to_replace}' was replaced with '{replacement}'."


openai_tools: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of the file",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to the file",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["name", "content"],
            },
        },
    },
]

# See https://docs.anthropic.com/en/docs/build-with-claude/tool-use
claude_tools: List[Dict[str, Any]] = [
    {
        "name": "get_dependencies",
        "description": "Get the dependency graph for one or more Python modules",
        "input_schema": {
            "type": "object",
            "properties": {
                "module_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of module names to get dependencies for",
                },
            },
            "required": ["module_names"],
        },
    },
    {
        "name": "read_file",
        "description": "Read the contents of the file of given name",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
            },
            "required": ["name"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to the file of given name",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of the file to edit."},
                "content": {
                    "type": "string",
                    "description": "New contents of the file.",
                },
            },
            "required": ["name", "content"],
        },
    },
    {
        "name": "ask_user",
        "description": "Ask the user a question and return their response",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The prompt to show the user",
                }
            },
            "required": ["prompt"],
        },
    },
    {
        "name": "replace_in_file",
        "description": "Replace a specific string in a file with another string",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of the file to edit."},
                "to_replace": {
                    "type": "string",
                    "description": "The string to be replaced.",
                },
                "replacement": {
                    "type": "string",
                    "description": "The string to replace with.",
                },
            },
            "required": ["name", "to_replace", "replacement"],
        },
    },
    {
        "name": "rename_file",
        "description": "Rename a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "old_name": {
                    "type": "string",
                    "description": "Current name of the file.",
                },
                "new_name": {"type": "string", "description": "New name for the file."},
            },
            "required": ["old_name", "new_name"],
        },
    },
    {
        "name": "delete_file",
        "description": "Delete a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the file to delete.",
                },
            },
            "required": ["name"],
        },
    },
    {
        "name": "create_file",
        "description": "Create a new file with optional content",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the file to create.",
                },
                "content": {
                    "type": "string",
                    "description": "Initial content of the file (optional).",
                },
            },
            "required": ["name"],
        },
    },
    {
        "name": "run_test",
        "description": "Run Python tests in a given file and return the results",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the test file to run.",
                },
            },
            "required": ["name"],
        },
    },
    {
        "name": "rg",
        "description": "Search for a pattern in files within the artifacts folder using ripgrep",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "The pattern to search for.",
                },
            },
            "required": ["pattern"],
        },
    },
    {
        "name": "exec",
        "description": "Execute a command in the terminal",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The command to execute."},
            },
            "required": ["command"],
        },
    },
]


def show_diff(original_file: str, modified_file: str) -> str:
    if os.path.exists(original_file) and os.path.exists(modified_file):
        subprocess.run(
            ["code", "--diff", original_file, modified_file],
            capture_output=True,
            text=True,
        )
    elif os.path.exists(modified_file):
        subprocess.run(["code", modified_file], capture_output=True, text=True)
    elif os.path.exists(original_file):
        print("File deleted.")
    else:
        raise Exception(
            f"Could not diff files. Neither file exists: {original_file} and {modified_file}"
        )


def rename_file(old_name: str, new_name: str, agent: AgentName) -> str:
    old_path = make_file_path(old_name, agent)
    new_path = make_file_path(new_name, agent)

    if not os.path.exists(old_path):
        raise FileNotFoundError(f"The file {old_name} does not exist.")

    # Create the directory for the new file if it doesn't exist
    new_dir = os.path.dirname(new_path)
    os.makedirs(new_dir, exist_ok=True)

    if os.path.exists(new_path):
        raise FileExistsError(f"The file {new_name} already exists.")

    os.rename(old_path, new_path)


def delete_file(name: str, agent: AgentName) -> str:
    file_path = make_file_path(name, agent)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {name} does not exist.")

    os.remove(file_path)


def create_file(name: str, agent: AgentName, content: str = "") -> str:
    file_path = make_file_path(name, agent)

    if os.path.exists(file_path):
        raise FileExistsError(f"The file {name} already exists.")

    # Create the directory for the new file if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w") as file:
        file.write(content)


def run_test(name: str, agent: AgentName) -> Dict[str, str]:
    file_path = make_file_path(name, agent)

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


def rg(pattern: str, agent: AgentName) -> str:
    try:
        result = subprocess.run(
            ["rg", "-i", pattern, artifacts_dir],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:  # No matches found
            return "No matches found."
        else:
            raise Exception(f"Error occurred: {e.stderr}")


# Set to store approved commands
approved_commands = set()


def exec(command: str, agent: AgentName) -> Dict[str, str]:
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
        error_message = f"Command execution failed with return code {e.returncode}.\n"
        error_message += f"Command: {modified_command}\n"
        error_message += f"Stdout: {e.stdout}\n"
        error_message += f"Stderr: {e.stderr}"
        raise Exception(error_message)


def get_dependencies(module_names: List[str]) -> Dict[str, List[str]]:
    module_paths = [
        os.path.join(artifacts_dir, f"{module}.py") for module in module_names
    ]
    dependency_graph = DependencyGraph(module_paths)
    return {
        module.name: [dep.name for dep in module.dependencies]
        for module in dependency_graph.modules.values()
    }


def handle_claude_tool_call(
    agent: AgentName,
    id: any,
    function_name: str,
    input: Dict[str, Any],
    modified_files: Set[str],
) -> List[Dict[str, Any]]:
    # print(f"TOOL_USE: {function_name} {input}")
    result = {"type": "tool_result", "tool_use_id": id}
    try:
        if function_name == "get_dependencies":
            dependency_graph = get_dependencies(input["module_names"])
            result["content"] = dependency_graph
        elif function_name == "read_file":
            content = read_file(input["name"], agent)
            result["content"] = content
        elif function_name == "write_file":
            if "content" not in input:
                raise Exception("write_file expects a content parameter.")
            write_file(
                input["name"],
                agent,
                input["content"],
            )
            modified_files.add(input["name"])
        elif function_name == "ask_user":
            result["content"] = ask_user(input["prompt"])
        elif function_name == "replace_in_file":
            replace_in_file(
                input["name"],
                agent,
                input["to_replace"],
                input["replacement"],
            )
            modified_files.add(input["name"])
        elif function_name == "rename_file":
            rename_file(
                input["old_name"],
                input["new_name"],
                agent,
            )
            modified_files.add(input["old_name"])
            modified_files.add(input["new_name"])
        elif function_name == "delete_file":
            delete_file(
                input["name"],
                agent,
            )
            modified_files.add(input["name"])
        elif function_name == "create_file":
            content = input.get("content", "")
            create_file(
                input["name"],
                agent,
                content,
            )
            modified_files.add(input["name"])
        elif function_name == "run_test":
            test_result = run_test(input["name"], agent)
            result["content"] = f"Test results for {input['name']}:\n"
            result["content"] += f"Return code: {test_result['returncode']}\n"
            result["content"] += f"Stdout:\n{test_result['stdout']}\n"
            result["content"] += f"Stderr:\n{test_result['stderr']}"
            print(result["content"])  # Show test results to the user
        elif function_name == "rg":
            result["content"] = rg(input["pattern"], agent)
        elif function_name == "exec":
            exec_result = exec(input["command"], agent)
            result["content"] = f"Command execution results:\n"
            result["content"] += f"Stdout:\n{exec_result['stdout']}\n"
            result["content"] += f"Stderr:\n{exec_result['stderr']}"
        else:
            raise Exception(f"Unknown function: {function_name}")
        # if "content" in result and len(result["content"]) > MAX_
    except Exception as err:
        print(f"TOOL CALL ERROR: {traceback.format_exc()}")
        result["is_error"] = True
        result["content"] = str(err)
    return result
