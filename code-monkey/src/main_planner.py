import os
import argparse
from agents.agents import Coder
from constants import load_environment, get_src_dir
from instrumentation import instrument, initialize_tracer
from util.logs import setup_logging

# NB(toshok) this starts the root span for a given conversation involving
# potentionally multiple agents and possibly several prompts per agent.  In a
# agent-as-process model, this would instead be the request handler for the
# agent.
@instrument("planner")
def main(debug: bool = False) -> None:
    print("DEBUG", debug)
    setup_logging(debug)

    coder = Coder(os.getenv("AI_MSN"))
    coder.initialize()

    # Read prompt from .prompt.md file
    with open(os.path.join(get_src_dir(), ".prompt.md"), "r") as prompt_file:
        prompt = prompt_file.read()

    coder.run_prompt(prompt)
    print("DONE")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run main_planner with optional debug logging")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    load_environment()

    initialize_tracer(
        {
            "agent": "Coder",
        }
    )
    main(debug=args.debug)