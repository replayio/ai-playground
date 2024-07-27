import asyncio
import os
from agents.agents import CodeAnalyst, run_agent_main


async def main() -> None:
    await run_agent_main(CodeAnalyst)


if __name__ == "__main__":
    asyncio.run(main())
    os._exit(0)
