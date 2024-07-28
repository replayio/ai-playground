import os
import argparse
import asyncio
from rich import print
from rich.console import Console
from simple_term_menu import TerminalMenu
from agents.agents import Coder, CodeAnalyst, Manager
from constants import load_environment, get_src_dir
from instrumentation import instrument, initialize_tracer
from util.logs import setup_logging

console = Console()


@instrument("main")
async def main(debug: bool = False) -> None:
    setup_logging(debug)
    print("[bold green]Welcome to the AI Agent Selector![/bold green]")

    agent_choices = [
        ("Coder", Coder),
        ("CodeAnalyst", CodeAnalyst),
        ("Manager", Manager),
    ]

    menu_items = [f"{i+1}. {name}" for i, (name, _) in enumerate(agent_choices)]
    terminal_menu = TerminalMenu(menu_items, title="Choose an agent to run:")
    menu_entry_index = terminal_menu.show()

    if menu_entry_index is None:
        print("[bold red]No selection made. Exiting...[/bold red]")
        return

    agent_name, agent_class = agent_choices[menu_entry_index]
    console.print(f"[bold blue]Running {agent_name} agent...[/bold blue]")

    agent = agent_class(os.getenv("AI_MSN"))
    agent.initialize()

    # Read prompt from .prompt.md file
    with open(os.path.join(get_src_dir(), ".prompt.md"), "r") as prompt_file:
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
            "agent": "Coder",
        }
    )
    asyncio.run(main(debug=args.debug))
    os._exit(0)
