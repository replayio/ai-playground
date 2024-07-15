import os
import shutil
import traceback
from enum import Enum
from typing import List, Dict, Any


class AgentName(Enum):
    Openai = 1
    Claude = 2


this_dir = os.path.dirname(os.path.abspath(__file__))
artifacts_dir = os.path.join(this_dir, "..", "artifacts")


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
    with open(file_path, "w") as file:
        file.write(content)


def copy_src() -> List[str]:
    dest_dir = artifacts_dir
    copied_files = []

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for item in os.listdir(this_dir):
        s = os.path.join(this_dir, item)
        d = os.path.join(dest_dir, item)
        if os.path.isfile(s):
            shutil.copy2(s, d)
            copied_files.append(item)

    return copied_files


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

claude_tools: List[Dict[str, Any]] = [
    {
        "name": "read_file",
        "description": "Read the contents of the file",
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
        "description": "Write content to the file",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["name", "content"],
        },
    },
]


def handle_claude_tool_call(
    agent: AgentName, id: any, function_name: str, input: Dict[str, Any]
) -> List[Dict[str, Any]]:
    # print(f"TOOL_CALL: {function_name} {input}")
    result = {"type": "tool_result", "tool_use_id": id}
    try:
        if function_name == "read_file":
            content = read_file(input["name"], agent)
            result["content"] = content
        elif function_name == "write_file":
            write_file(
                input["name"],
                agent,
                input["content"],
            )
        else:
            raise Exception("Unknown function: {function_name}")
    except Exception as err:
        print(f"TOOL CALL ERROR: {traceback.format_exc()}")
        result["is_error"] = True
        result["content"] = str(err)
    return result
