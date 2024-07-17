import os
import shutil
import traceback
from enum import Enum
from typing import List, Dict, Set, Any
import subprocess


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


def copy_src() -> List[str]:
    dest_dir = artifacts_dir

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    try:
        shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)
    except Exception as e:
        print(f"Directory not copied. Error: {e}")

    relative_paths = []
    for root, dirs, files in os.walk(dest_dir):
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, dest_dir)
            relative_paths.append(relative_path)

    return relative_paths


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
]


def show_diff(original_file: str, modified_file: str) -> str:
    try:
        result = subprocess.run(
            ["code", "--diff", original_file, modified_file],
            capture_output=True,
            text=True,
        )
        return result.stdout
    except Exception as e:
        return f"Error showing diff: {str(e)}"


def handle_claude_tool_call(
    agent: AgentName,
    id: any,
    function_name: str,
    input: Dict[str, Any],
    modified_files: Set[str],
) -> List[Dict[str, Any]]:
    print(f"TOOL_USE: {function_name}")
    result = {"type": "tool_result", "tool_use_id": id}
    try:
        if function_name == "read_file":
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
            result["content"] = replace_in_file(
                input["name"],
                agent,
                input["to_replace"],
                input["replacement"],
            )
            modified_files.add(input["name"])
        else:
            raise Exception(f"Unknown function: {function_name}")
        # if "content" in result and len(result["content"]) > MAX_
    except Exception as err:
        print(f"TOOL CALL ERROR: {traceback.format_exc()}")
        result["is_error"] = True
        result["content"] = str(err)
    return result
