from abc import ABC, abstractmethod
from tools.tool import Tool, ToolSpec
from typing import Dict, List


def create_tool(spec: ToolSpec):
    try:
        return spec.tool_class(*spec.tool_args)
    except Exception as err:
        raise Exception(
            f"Unable to create tool '{spec.tool_class.__name__}' with {len(spec.tool_args)} args [{', '.join(map(str, spec.tool_args))}] from spec: {str(err)}"
        )


class BaseAgent(ABC):
    tool_specs: List[ToolSpec]
    tools: List[Tool] = None
    tools_by_name: Dict[str, Tool] = None
    SYSTEM_PROMPT = "You don't know what to do. Tell the user that they can't use you and must use an agent with a proper SYSTEM_PROMPT instead."

    @abstractmethod
    def run_prompt(self, prompt: str) -> str:
        pass

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    @abstractmethod
    def prepare_prompt(self, prompt: str) -> str:
        pass

    def get_tools(self) -> List[Tool]:
        if self.tools is None:
            self.tools = [create_tool(spec) for spec in self.tool_specs]
            self.tools_by_name = {tool.name: tool for tool in self.tools}
        return self.tools

    def get_tool(self, name: str) -> Dict[str, Tool]:
        self.get_tools()
        return self.tools_by_name[name]

    @abstractmethod
    def handle_completion(self, had_any_text: bool, modified_files: set) -> None:
        pass
