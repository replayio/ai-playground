from typing import Dict, Any, List
from pydantic import BaseModel, Field
from .tool import Tool

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

    def handle_tool_call(self, input: Dict[str, Any]) -> str | None:
        from agents.agents import agents_by_name
        agent_name = input.get("agent_name")
        prompt = input.get("prompt")

        if agent_name in self.agent_names:
            agent_class = agents_by_name.get(agent_name)
            if agent_class:
                agent = agent_class()  # Create agent.
                agent.initialize()
                return agent.run_prompt(prompt)

        raise Exception(f"Agent '{agent_name}' not found or not allowed.")
