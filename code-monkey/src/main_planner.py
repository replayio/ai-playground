import os
from agents.agents import Coder
from constants import load_environment
from instrumentation import instrument, initialize_tracer


# NB(toshok) this starts the root span for a given conversation involving
# potentionally multiple agents and possibly several prompts per agent.  In a
# agent-as-process model, this would instead be the request handler for the
# agent.
@instrument("planner")
def main() -> None:
    print("Initializing...")

    coder = Coder(os.getenv("AI_MSN"))
    coder.initialize()

    print("Go...\n")

    prompt = """
1. Modify planner.py to read the prompt value from a local `.prompt.md`, next to the planner.py file.
"""
    coder.run_prompt(prompt)


if __name__ == "__main__":
    load_environment()

    initialize_tracer(
        {
            "agent": "Coder",
        }
    )
    main()
