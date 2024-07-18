from typing import Dict, Type
from .tools import tools_by_name
from ..agent import Agent

class InvokeAgentTool:
    """
    A tool for invoking other agents by name and running them with a given prompt.
    """

    def __init__(self):
        self.agents_by_name: Dict[str, Type[Agent]] = {
            name: tool for name, tool in tools_by_name.items()
            if isinstance(tool, type) and issubclass(tool, Agent)
        }

    def __call__(self, agentName: str, prompt: str) -> str:
        agent_class = self.agents_by_name.get(agentName)
        if agent_class:
            agent = agent_class()
            return agent.run(prompt)
        else:
            return f"Agent '{agentName}' not found."