import traceback
from typing import List, Dict, Set, Any, Type

from tools.tool import Tool
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


def get_tool_spec(tool_class: Tool) -> Dict[str, Any]:
    return {
        "name": tool_class.name,
        "description": tool_class.description,
        "input_schema": tool_class.input_schema,
    }

def get_tool_specs(tool_classes: List[Tool]):
    return [get_tool_spec(tool) for tool in tool_classes]


all_tool_classes = [
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

tool_classes_by_name: Dict[str, Type[Tool]] = {tool.__name__: tool for tool in all_tool_classes}


def handle_tool_call(
    id: any,
    input: Dict[str, Any],
    modified_files: Set[str],
    tool: Tool,
) -> List[Dict[str, Tool]]:
    result = {"type": "tool_result", "tool_use_id": id}
    try:
        # Call the handle_tool_call method on the instance
        call_result = tool.handle_tool_call(input)
        result["content"] = call_result

        # Add modified files to the parameter
        if isinstance(tool, IOTool):
            modified_files.update(tool.modified_files)
            tool.clear_modified_files()

    except Exception as err:
        print(f"TOOL CALL ERROR: {traceback.format_exc()}")
        result["is_error"] = True
        result["content"] = str(err)
    return result

