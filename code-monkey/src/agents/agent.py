import os
from typing import Set, Any
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage

from tools.utils import (
    ask_user,
    show_diff,
)
from constants import get_root_dir, get_artifacts_dir, get_agent_msn
from models import MSN
from .base_agent import BaseAgent
from instrumentation import current_span, instrument
from langgraph.checkpoint.aiosqlite import AsyncSqliteSaver

from util.logs import get_logger

class Agent(BaseAgent):
    # trying to figure out how to type this.  It's not a BaseChatModel, it's a
    # CompiledGraph from langgraph.graph, but that's not exported
    model: Any

    config = {
        "configurable": {"thread_id": "abc123"},
    }

    @instrument("Agent.__init__", ["msn_str"])
    def __init__(self):
        msn_str = get_agent_msn()
        msn = MSN.from_string(msn_str)

        # a checkpointer + the thread_id below gives the model a way to save its
        # state so we don't have to accumulate the messages ourselves.
        memory = AsyncSqliteSaver.from_conn_string(":memory:")
        self.model = create_react_agent(
            msn.construct_model(),
            self.tools,
            checkpointer=memory,
        )
        self.initialize()

    # Custom Agent initialization goes here, when necessary.
    def initialize(self):
        pass

    def prepare_prompt(self, prompt: str) -> str:
        return prompt

    @instrument("Agent.run_prompt", ["prompt"])
    async def run_prompt(self, prompt: str) -> str:
        logger = get_logger(__name__)
        logger.info(f"Running prompt: {prompt}")

        system = SystemMessage(content=self.get_system_prompt())
        msg = HumanMessage(content=self.prepare_prompt(prompt))

        modified_files: Set[str] = set()
        logger = get_logger(__name__)
        
        result: str | None = None

        async for event in self.model.astream_events(
            {
                "messages": [system, msg],
            },
            self.config,
            version="v2",
        ):
            kind = event["event"]

            if kind != "on_chat_model_stream" and kind != "on_chain_end" and kind != "on_chain_stream" and kind != "on_chain_start":
                logger.debug(f"[AGENT {self.name}] received event: {kind}")

            if kind == "on_chat_model_start":
                # for msg in event["data"]["input"]["messages"][0]:
                #     print("----")
                #     print(msg.content)
                continue

            if kind == "on_chat_model_stream":
                # NB(toshok) we can stream text as it comes in by doing it here,
                # but I'm doing the entire thing in one go in the
                # on_chat_model_end event just below.
                continue

            if kind == "on_tool_start":
                tool_name = event["name"]
                tool_input = event["data"]["input"]
                logger.debug(f"tool start - name={tool_name}, input={repr(tool_input)}")
                continue

            if kind == "on_tool_end":
                logger.debug("----")
                tool_name = event["name"]
                tool_output = event["data"]["output"].content[:20]
                logger.debug(f"[AGENT {self.name}] tool end - name={tool_name}, output={repr(tool_output)}")
                continue

            if kind == "on_chat_model_end":
                if isinstance(event["data"]["output"].content, list):
                    # anthropic seems give us content as a list?
                    result = event["data"]["output"].content[0]["text"]
                else:
                    result = event["data"]["output"].content
                print(f"[AGENT {self.name}]" + result)
                # TODO(toshok) still need to compute tokens
                continue

            if kind == "on_custom_event":
                # TODO(toshok) a better dispatch mechanism would be nice, but
                # there's only one event type currently
                if event["name"] == "file_modified":
                    modified_files.add(event["data"])
                else:
                    logger.debug(f"[AGENT {self.name}] Unknown prompt event: '{event["name"]}'")
                continue

        self.handle_completion(
            modified_files,
        )

        # TODO(toshok) we aren't returning a result here, and likely should...
        logger.debug(f"[AGENT {self.name}] run_prompt result: \"{result or ""}\"")
        return result or ""

    @instrument("Agent.handle_completion")
    def handle_completion(self, modified_files: set) -> None:
        current_span().set_attributes(
            {
                "num_modified_files": len(modified_files),
                "modified_files": str(modified_files),
            }
        )

        if modified_files:
            for file in modified_files:
                self.handle_modified_file(file)

    @instrument("Agent.handle_modified_file", ["file"])
    def handle_modified_file(self, file: str) -> None:
        original_file = os.path.join(get_root_dir(), file)
        modified_file = os.path.join(get_artifacts_dir(), file)
        show_diff(original_file, modified_file)
        response = ask_user(
            f"Do you want to apply the changes to {file} (diff shown in VSCode)? (Y/n): "
        ).lower()

        apply_changes = response == "y" or response == ""

        current_span().set_attribute("apply_changes", apply_changes)

        if apply_changes:
            self.apply_changes(original_file, modified_file)
            print(f"✅ Changes applied to {file}")
        else:
            print(f"❌ Changes not applied to {file}")

    @instrument("Agent.apply_changes", ["original_file", "modified_file"])
    def apply_changes(self, original_file: str, modified_file: str) -> None:
        # TODO(toshok) we probably want the before/after size?  or something about size of the diff
        with open(modified_file, "r") as modified, open(original_file, "w") as original:
            original.write(modified.read())
