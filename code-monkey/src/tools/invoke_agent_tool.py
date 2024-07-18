from typing import Dict, Any, List
from pydantic import BaseModel, Field
from .tool import Tool
from ..agent import Agent
from ..agents import agents_by_name

class InvokeAgentInput(BaseModel):
    agent_name: str = Field(..., description="Name of the agent to invoke")
    prompt: str = Field(..., description="Prompt to run with the agent")

class InvokeAgentTool(Tool):
    """
    A tool for invoking other agents by name and running them with a given prompt.
    """
    name = "invoke_agent"
    description = "Invokes another agent by name and runs it with a given prompt"
    input_schema = InvokeAgentInput

    def __init__(self, agent_names: List[str]):
        super().__init__()
        self.agent_names = agent_names

    def handle_tool_call(self, input: Dict[str, Any]) -> Dict[str, Any] | None:
        agent_name = input.get("agent_name")
        prompt = input.get("prompt")

        if agent_name in self.agent_names:
            agent_class = agents_by_name.get(agent_name)
            if agent_class:
                agent = agent_class([])  # Pass an empty list for now
                result = agent.run_prompt(prompt)
                return {"result": result}

        return {"error": f"Agent '{agent_name}' not found or not allowed."}