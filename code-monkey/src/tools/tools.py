import traceback
from typing import List, Dict, Set, Any, Type
from enum import Enum

from tools.tool import Tool
from tools.get_dependencies_tool import GetDependenciesTool
from tools.read_file_tool import ReadFileTool
from tools.write_file_tool import WriteFileTool
from tools.ask_user_tool import AskUserTool
from tools.replace_in_file_tool import ReplaceInFileTool
from tools.rename_file_tool import RenameFileTool
from tools.delete_file_tool import DeleteFileTool
from tools.create_file_tool import CreateFileTool
from tools.run_test_tool import RunTestTool
from tools.rg_tool import RgTool
from tools.exec_tool import ExecTool
from tools.io_tool import IOTool
from tools.invoke_agent_tool import InvokeAgentTool


class AgentName(Enum):
    Openai = 1
    Claude = 2


def get_tool_spec(tool_class: Type[Tool]) -> Dict[str, Any]:
    return {
        "name": tool_class.name,
        "description": tool_class.description,
        "input_schema": tool_class.input_schema,
    }


all_tool_classes = [
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
    InvokeAgentTool,
]

tools_by_name: Dict[str, Type[Tool]] = {tool.name: tool for tool in all_tool_classes}

claude_tools: List[Dict[str, Any]] = [get_tool_spec(tool) for tool in all_tool_classes]


def handle_claude_tool_call(
    agent: AgentName,
    id: any,
    function_name: str,
    input: Dict[str, Any],
    modified_files: Set[str],
) -> List[Dict[str, Any]]:
    result = {"type": "tool_result", "tool_use_id": id}
    try:
        tool_class = tools_by_name.get(function_name)
        if tool_class is None:
            raise Exception(f"Unknown function: {function_name}")

        # Instantiate the tool
        tool_instance = tool_class()

        # Call the handle_tool_call method on the instance
        call_result = tool_instance.handle_tool_call(input)
        result["content"] = call_result

        # Add modified files to the parameter
        if isinstance(tool_instance, IOTool):
            modified_files.update(tool_instance.modified_files)
            tool_instance.clear_modified_files()

    except Exception as err:
        print(f"TOOL CALL ERROR: {traceback.format_exc()}")
        result["is_error"] = True
        result["content"] = str(err)
    return result