import logging
import traceback
from typing import Type, List, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.callbacks import (
    CallbackManagerForToolRun,
    AsyncCallbackManagerForToolRun,
    dispatch_custom_event,
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
    allowed_agents: List[str]
    
    def __init__(self, allowed_agents: List[str], **kwargs):
        super().__init__(
            name="invoke_agent",
            description=f"Invokes the any of the following agents by name with a given prompt: {str(allowed_agents)}",
            args_schema=InvokeAgentInput,
            allowed_agents=allowed_agents,
            **kwargs
        )
        print(f"DDBG InvokeAgentTool: {self.description}")

    @instrument(
        "Tool._run", ["agent_name", "prompt"], attributes={"tool": "InvokeAgentInput"}
    )
    def _run(
        self,
        agent_name: str,
        prompt: str,
        run_manager: Optional[CallbackManagerForToolRun],
    ) -> None:
        raise NotImplementedError("invoke_agent does not support sync")

    async def _arun(
        self,
        agent_name: str,
        prompt: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun],
    ) -> None:
        try:
            from agents.service import services_by_agent_name

            if agent_name not in self.allowed_agents:
                raise Exception(f"Agent '{agent_name}' not found or not allowed.")

            service = services_by_agent_name[agent_name]

            # send a prompt, then wait for a response
            await service.send_to({"prompt": prompt})

            response = await service.receive_from()

            # emit a custom event with the response
            dispatch_custom_event("agent_response", response)
        except Exception:
            logging.error("Failed to invoke agent: %s", agent_name)
            traceback.print_exc()
            # Re-raise the exception
            raise
