import os
from typing import List, Dict
from tools.tool import Tool
from abc import ABC, abstractmethod
from typing import Type, Any

from tools.utils import (
    ask_user,
    show_diff,
    src_dir,
    artifacts_dir,
)


class ToolSpec:
    def __init__(self, tool_class: Type[Tool], tool_args: List[Any]):
        self.tool_class = tool_class
        self.tool_args = tool_args


class BaseAgent(ABC):
    tool_specs: List[ToolSpec]
    tools: List[Tool]
    tools_by_name: Dict[str, Tool]
    SYSTEM_PROMPT = "You don't know what to do. Tell the user that they can't use you and must use an agent with a proper SYSTEM_PROMPT instead."

    @abstractmethod
    def run_prompt(self, prompt: str) -> str:
        pass

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    @abstractmethod
    def prepare_prompt(self, prompt: str) -> str:
        pass

    def get_tools(self) -> Dict[str, Tool]:
        if not self.tools:
            self.tools = [
                spec.tool_class(self, *spec.tool_args) for spec in self.tool_specs
            ]
            self.tools_by_name = {
                tool.name: tool
                for tool in self.tools
            }
        return self.tools_by_name
    
    def get_tool(self, name: str) -> Dict[str, Tool]:
        self.get_tools()
        return self.tools_by_name[name]

    def handle_completion(self, had_any_text: bool, modified_files: set) -> None:
        if not had_any_text:
            print("Done.")

        if modified_files:
            print(f"Modified files: {', '.join(modified_files)}")
            for file in modified_files:
                self._handle_modified_file(file)
        return True

    def _handle_modified_file(self, file: str) -> None:
        original_file = os.path.join(src_dir, file)
        modified_file = os.path.join(artifacts_dir, file)
        show_diff(original_file, modified_file)
        apply_changes = ask_user(
            f"Do you want to apply the changes to {file} (diff shown in VSCode)? (Y/n): "
        ).lower()
        if apply_changes == "y" or apply_changes == "":
            self._apply_changes(original_file, modified_file)
            print(f"✅ Changes applied to {file}")
        else:
            print(f"❌ Changes not applied to {file}")

    def _apply_changes(self, original_file: str, modified_file: str) -> None:
        with open(modified_file, "r") as modified, open(original_file, "w") as original:
            original.write(modified.read())
