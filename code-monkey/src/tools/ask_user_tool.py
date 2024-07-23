from pydantic import BaseModel, Field
from typing import Type, Optional
from langchain_core.tools import BaseTool
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
)
from instrumentation import instrument

class AskUserToolInput(BaseModel):
    prompt: str = Field(description="The prompt to show the user")

class AskUserTool(BaseTool):
    """Tool to ask the user a question and wait for their response"""
    name: str = "ask_user"
    description: str = "Ask the user a question and return their response"
    args_schema: Type[BaseModel] = AskUserToolInput

    @instrument("Tool._run", ["prompt"], attributes={ "tool": "AskUserTool" })
    def _run(self, prompt: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        print(prompt)
        response = input()
        return response