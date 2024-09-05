import os
import argparse
import asyncio
from rich import print
from rich.console import Console
from agents.agents import Manager
from constants import load_environment, get_root_dir
from instrumentation import instrument, initialize_tracer
from util.logs import setup_logging

console = Console()


@instrument("main")
async def main(debug: bool = False) -> None:
    setup_logging(debug)
    print("[bold green]Welcome to the AI Playground![/bold green]")

    console.print("[bold blue]Running Manager agent...[/bold blue]")

    agent = Manager()
    agent.initialize()

    # Read prompt from .prompt.md file
    with open(os.path.join(get_root_dir(), ".prompt.md"), "r") as prompt_file:
        prompt = prompt_file.read()

    await agent.run_prompt(prompt)
    console.print("[bold green]DONE[/bold green]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run main with optional debug logging")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    load_environment()

    initialize_tracer(
        {
            "agent": "Manager",
        }
    )
    asyncio.run(main(debug=args.debug))
    os._exit(0)
