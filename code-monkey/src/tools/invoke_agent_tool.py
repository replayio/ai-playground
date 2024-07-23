from typing import Type, List, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
)
from instrumentation import instrument

class InvokeAgentInput(BaseModel):
    agent_name: str = Field(description="Name of the agent to invoke")
    prompt: str = Field(description="Prompt to run with the agent")

class InvokeAgentTool(BaseTool):
    """
    A tool for invoking other agents by name and running them with a given prompt.
    """
    name: str = "invoke_agent"
    description: str = "Invokes another agent by name and runs it with a given prompt"
    args_schema: Type[BaseModel] = InvokeAgentInput

#    agent_names: List[str]

    def __init__(self, agent_names: List[str]):
#        self.agent_names = agent_names
        pass

    @instrument("Tool._run", ["agent_name", "prompt"], attributes={ "tool": "InvokeAgentInput" })
    def _run(self, agent_name: str, prompt: str, run_manager: Optional[AsyncCallbackManagerForToolRun])-> None:
        from agents.agents import agents_by_name
        if agent_name in self.agent_names:
            agent_class = agents_by_name.get(agent_name)
            if agent_class:
                agent = agent_class()  # Create agent.
                agent.initialize()
                return agent.run_prompt(prompt)

        raise Exception(f"Agent '{agent_name}' not found or not allowed.")
