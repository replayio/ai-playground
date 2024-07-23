import os
from agents.agents import Coder
from constants import load_environment
from instrumentation import instrument, initialize_tracer

# NB(toshok) this starts the root span for a given conversation involving
# potentionally multiple agents and possibly several prompts per agent.  In a
# agent-as-process model, this would instead be the request handler for the
# agent.
@instrument("main")
def main() -> None:
    print("Initializing...")

    coder = Coder(os.getenv("AI_MSN"));
    coder.initialize()

    print("Go...\n")

    prompt = """Add a new embeddings/embeddings.py file with an Embeddings class:
1. The class should have a `read_files` function that takes a folder and uses the logic from copy_src in code_context.py to enumerate all files (respecting gitignore).
2. A sub class called VoyageEmbeddings should use that function to implement a new `embed` function that reads all those files and creates embeddings for them.
3. The Embeddings class should have a (maybe abstract) run_prompt(prompt: string) function that runs the prompt on the stored embeddings.
4. The VoyageEmbeddings class should implement that run_prompt function correspondingly.
"""
    coder.run_prompt(prompt)


if __name__ == "__main__":
    load_environment()

    initialize_tracer({
        "agent": "Coder",
    });

    main()
