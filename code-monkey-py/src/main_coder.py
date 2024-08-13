import asyncio
import os
from agents.agents import Coder, run_agent_main


async def main() -> None:
    await run_agent_main(Coder)


if __name__ == "__main__":
    asyncio.run(main())
    os._exit(0)
