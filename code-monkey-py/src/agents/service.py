# Wraps an agent in an asyncio loop and runs it.  Creates two queues for the agent to use for input and output.

import asyncio
from typing import Dict, Any

from agents.agent import Agent
from agents.agents import agents_by_name
from agents.typed_queue import TypedQueue

from util.logs import get_logger

type JSONDict = Dict[str, Any]


class AgentService:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.request_queue = TypedQueue[JSONDict]()
        self.response_queue = TypedQueue[JSONDict]()

    async def send_to(self, data: JSONDict) -> None:
        await self.request_queue.put(data)

    async def receive_from(self) -> JSONDict:
        return await self.response_queue.get()

    # private versions of get/put from the queues on the agent-side of things
    async def _send(self, data: JSONDict) -> None:
        await self.response_queue.put(data)

    async def _receive(self) -> JSONDict:
        return await self.request_queue.get()

    async def send_receive(self):
        logger = get_logger(__name__)
        while True:
            data = await self._receive()
            # assume that we're always getting a { "prompt": "..." } object, and that we're always returning a { "response": "..." } object
            logger.info(f"[Agent {self.agent.name}] received prompt: {data['prompt']}")
            response = await self.agent.run_prompt(data["prompt"])

            logger.info(f"[Agent {self.agent.name}] responding with: {response}")
            await self._send({"response": response})

    def run(self):
        return asyncio.create_task(self.send_receive())


class AgentServiceDict(dict):
    def __missing__(self, key: str) -> AgentService:
        AgentClass = agents_by_name[key]
        service = AgentService(AgentClass())

        service.run()  # do something with the return value here so we can gather them later?

        return service


services_by_agent_name = AgentServiceDict()
