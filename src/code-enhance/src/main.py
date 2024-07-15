import os
from typing import List
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic
# from pprint import pprint
from tools import (
    AgentName,
    handle_claude_tool_call,
    openai_tools,
    claude_tools,
    copy_src,
)

# Load environment variables from .env and .secret.env
load_dotenv()
load_dotenv(".env.secret")

# Load API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not OPENAI_API_KEY or not ANTHROPIC_API_KEY:
    raise ValueError(
        "API keys not found. Please check your .env and .secret.env files."
    )


class Agent:
    name: AgentName
    names: List[str]

    def __init__(self, names: List[str]) -> None:
        self.names = names

    def run_prompt(self, prompt: str) -> str:
        raise NotImplementedError("Subclasses must implement run_prompt method")

    def imbue_prompt(self, query: str) -> str:
        return f"""
These are all files: {self.names}. Only if you need to, read or write them with tools. Don't explain your actions.
Query: {query}
    """.strip()


class OpenAIAgent(Agent):
    name = AgentName.Openai

    def __init__(self) -> None:
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def run_prompt(self, prompt: str) -> str:
        messages = [{"role": "user", "content": prompt}]

        while True:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4-0125-preview",
                    messages=messages,
                    tools=openai_tools,
                    tool_choice="auto",
                )

                response_message = response.choices[0].message
                messages.append(response_message)

                if response_message.tool_calls:
                    tool_responses = handle_claude_tool_call(
                        response_message.tool_calls
                    )
                    messages.extend(tool_responses)
                else:
                    return response_message.content
            except Exception as e:
                return f"Error: {str(e)}"


class ClaudeAgent(Agent):
    name = AgentName.Claude

    def __init__(self, names: List[str]) -> None:
        super().__init__(names)
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)

    def run_prompt(self, prompt: str) -> str:
        prompt = prompt.strip()
        print(f"Q: \"{prompt}\"")
        prompt = self.imbue_prompt(prompt)
        messages = [{"role": "user", "content": prompt}]

        more = True
        had_any_text = False
        while more:
            # print("Sending messages:")
            # pprint(messages)
            response = self.client.messages.create(
                temperature=0,
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=messages,
                tools=claude_tools,
            )
            assistant_messages = []
            user_messages = []

            for response_message in response.content:
                # print("RESPONSE:")
                # pprint(response_message)
                assistant_messages.append(response_message)

                if response_message.type == "tool_use":
                    user_messages.append(
                        handle_claude_tool_call(
                            self.name,
                            response_message.id,
                            response_message.name,
                            response_message.input,
                        )
                    )
                elif response_message.type == "text":
                    had_any_text = True
                    print(f"A: {response_message.text}")
                elif response_message.type == "error":
                    had_any_text = True
                    return f"ERROR: {response_message.text}"
                elif response_message.type == "final":
                    had_any_text = True
                    return f"DONE: {str(response_message)}"
                else:
                    raise Exception(
                        f"Unhandled message type: {response_message.type} - {str(response_message)}"
                    )
            if len(user_messages) == 0:
                # No more replies: Done!
                more = False
            else:
                messages.append({"role": "assistant", "content": assistant_messages})
                messages.append({"role": "user", "content": user_messages})

        if not had_any_text:
            print("Done.")


def main() -> None:
    print("Initializing...")
    # openai_agent = OpenAIAgent()
    names = copy_src()
    claude_agent = ClaudeAgent(names)
    # names = []

    print("Go...\n")
    prompt = "Briefly summarize the contents of main.py."
    claude_agent.run_prompt(prompt)

    print("\n\n")

    prompt = "Write a hello world program into main.py."
    claude_agent.run_prompt(prompt)

    print("\n\n")

    prompt = "Summarize the contents of main.py."
    claude_agent.run_prompt(prompt)


if __name__ == "__main__":
    main()
