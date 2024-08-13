import os
import argparse
from typing import List, Type
from tools import (
    AskUserTool,
    CreateFileTool,
    DeleteFileTool,
    ExecTool,
    InvokeAgentTool,
    ReadFileTool,
    RenameFileTool,
    ReplaceInFileTool,
    RunTestTool,
    WriteFileTool,
    CAImportsTool,
    CAExportsTool,
    CAASTAnalyzerTool,
    CADependencyGraphTool,
)
from code_context import CodeContext, getDefaultCodeContext
from .agent import Agent
from constants import load_environment, get_root_dir
from instrumentation import initialize_tracer, instrument
from util.logs import setup_logging



class EngineeringPlanner(Agent):
    name = "EngineeringPlanner"
    SYSTEM_PROMPT = """
1. You are a planner agent.
2. You are responsible for converting high-level user tasks into much smaller and more specific engineering tasks for engineers to carry out.
3. You are also responsible for communicating with the user on interface design questions, whenever there are gaps.
4. You are always suspicious that requirements are incomplete.
5. You always try to find proof for requirement completeness before jumping to conclusions.
6. You are enthusiastic about working with the user on making sure that all requirements are understood and implemented.
7. When breaking down tasks, consider grouping related changes to minimize redundant work by the Coder.
"""
    tools = [
        InvokeAgentTool(allowed_agents=["Engineer"]),
    ]


class Engineer(Agent):
    name = "Engineer"
    SYSTEM_PROMPT = """
1. You are an engineering brain.
2. Take on one engineering task at a time. Each task should be limited to specific code locations.
3. Delegate the actual coding to the coder agent.
4. Delegate testing or running of programs to a debugger agent.
5. When you receive reports from coder and debugger agents, you determine whether your job is done or whether more work is required.
6. Upon reviewing reports you check for task completeness. As long as there are more obvious tasks, you ask the CodeAnalyst agent to find relevant code locations, and then ask the coder to change them, and/or the debugger to test them.
7. TODO: Implement a mechanism to subdivide engineering tasks into smaller tasks upon discovery.
8. Provide clear and detailed instructions to the Coder agent to minimize the need for clarifications.
"""
    tools = [
        InvokeAgentTool(allowed_agents=["CodeAnalyst", "Coder", "Debugger"]),
    ]


class CodeAnalyst(Agent):
    name = "CodeAnalyst"
    SYSTEM_PROMPT = """
1. You are the CodeAnalyst agent, responsible for deep code analysis and understanding.
2. Use tools to provide comprehensive insights about the codebase.
3. Focus on identifying code locations that require changes or investigations, based on given requirements.
4. Provide detailed context and relationships between code elements.
5. Present your findings in a structured format that can be easily parsed and utilized by other agents.
"""
    tools = [
        ReadFileTool(),
        CAImportsTool(),
        CAExportsTool(),
        CAASTAnalyzerTool(),
        CADependencyGraphTool(),
    ]


class Coder(Agent):
    name = "Coder"
    context: CodeContext
    SYSTEM_PROMPT = """
1. You are a programming agent who implements code changes based on very clear specifications.
2. You should only change the functions, classes or other code that have been specifically mentioned in the specs. Don't worry about changing anything else.
3. Use tools only if necessary.
4. Don't retry failed commands.
5. For simpler tasks, you have the autonomy to make decisions and implement changes without consulting other agents.
"""
    tools = [
        # TODO: These tool specs are about 1k tokens.
        ReadFileTool(),
        WriteFileTool(),
        CreateFileTool(),
        RenameFileTool(),
        DeleteFileTool(),
        ReplaceInFileTool(),
    ]

    def initialize(self):
        self.set_context(getDefaultCodeContext())

    def set_context(self, context: CodeContext):
        self.context = context

    def prepare_prompt(self, prompt: str) -> str:
        # TODO: known_files cost several hundred tokens for a small project.
        return f"""
These are all files: {self.context.known_files}.
Query: {prompt.strip()}
    """.strip()


class Debugger(Agent):
    name = "Debugger"
    SYSTEM_PROMPT = """
1. You are "Tester", an agent responsible for running tests and executing commands.
2. Use the RunTestTool to run tests and the ExecTool to execute commands when necessary.
3. Report test results and execution outputs clearly and concisely.
4. If a test fails or a command execution encounters an error, provide detailed information about the failure or error.
5. Suggest potential fixes or next steps based on test results or command outputs.
6. Provide feedback to the Coder agent on common issues or patterns observed during testing to help improve code quality.
"""
    tools = [
        RunTestTool(),
        ExecTool(),
        #        InvokeAgentTool(allowed_agents=["Coder"]),
    ]

    def initialize(self):
        self.set_context(getDefaultCodeContext())

    def set_context(self, context: CodeContext):
        self.context = context

    def prepare_prompt(self, prompt: str) -> str:
        # TODO: known_files cost several hundred tokens for a small project.
        return f"""
These are all files: {self.context.known_files}.
Query: {prompt.strip()}
    """.strip()


class Manager(Agent):
    name = "Manager"
    SYSTEM_PROMPT = """
1. You are the manager, a high-level agent capable of delegating tasks and coordinating other agents.
2. You do not read/write files or do any engineering work on your own.  Instead you delegate that work to other agents, and liase with the user, either through direct messages or through github PR comments.
2. Prefix negative responses with "❌". Prefix responses that indicate a significant success with "✅". Don't prefix neutral responses.
3. Use tools only if necessary.
4. Start by laying out a plan of all individual steps.
5. Make sure to finish all steps!
6. If you have low confidence in a response or don't understand an instruction, explain why and ask the user for clarification.
7. If the response from engineering is acceptable, relay it to the user.
"""
    tools = [
        # InvokeAgentTool(allowed_agents=["EngineeringPlanner"]),
        InvokeAgentTool(allowed_agents=["Coder"]),
        AskUserTool(),
    ]

    def initialize(self):
        self.set_context(getDefaultCodeContext())

    def set_context(self, context: CodeContext):
        self.context = context

    def prepare_prompt(self, prompt: str) -> str:
        # TODO: known_files cost several hundred tokens for a small project.
        return f"""
These are all files: `[{self.context.known_files}]`.
Query: {prompt.strip()}
    """.strip()


agents: List[Type[Agent]] = [Manager, EngineeringPlanner, CodeAnalyst, Coder, Debugger]
agents_by_name = {agent.__name__: agent for agent in agents}


@instrument("run_agent_impl")
async def _run_agent_impl(agent_class: Type[Agent]):
    parser = argparse.ArgumentParser(
        description="Run main_planner with optional debug logging"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    setup_logging(args.debug)

    load_environment()

    # Initialize agent.
    agent = agent_class()
    agent.initialize()

    # Read prompt from .prompt.md file
    with open(os.path.join(get_root_dir(), ".prompt.md"), "r") as prompt_file:
        prompt = prompt_file.read()

    await agent.run_prompt(prompt)
    print("DONE")


async def run_agent_main(agent_class: Type[Agent]):
    initialize_tracer(
        {
            "agent": agent_class.__name__,
        }
    )
    await _run_agent_impl(agent_class)
