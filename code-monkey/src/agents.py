from typing import Dict, List, Tuple
from agent import Agent, ToolUser
from tools.invoke_agent_tool import InvokeAgentTool
from tools.read_file_tool import ReadFileTool
from tools.write_file_tool import WriteFileTool
from tools.create_file_tool import CreateFileTool
from tools.rename_file_tool import RenameFileTool
from tools.delete_file_tool import DeleteFileTool
from tools.replace_in_file_tool import ReplaceInFileTool
from tools.ask_user_tool import AskUserTool
from tools.run_test_tool import RunTestTool
from tools.exec_tool import ExecTool

def make_coder(base_agent: Agent) -> Agent:
    class Coder(base_agent):
        SYSTEM_PROMPT = """
    1. You are "Code Monkey", a programming agent who tries to comprehend and fix programming problems.
    2. Prefix negative responses with "❌". Prefix responses that indicate a significant success with "✅". Don't prefix neutral responses.
    3. Use tools only if necessary.
    4. If you have low confidence in a response or don't understand an instruction, explain why and use the ask_user tool to gather clarifications.
    5. Don't retry failed commands.
    6. Don't make white-space-only changes to files.
    7. Don't suppress Exceptions.
    """
        tools = [
            ToolUser(ReadFileTool, []),
            ToolUser(WriteFileTool, []),
            ToolUser(CreateFileTool, []),
            ToolUser(RenameFileTool, []),
            ToolUser(DeleteFileTool, []),
            ToolUser(ReplaceInFileTool, []),
        ]

    return Coder

def make_master(base_agent: Agent) -> Agent:
    class Master(base_agent):
        SYSTEM_PROMPT = """
    1. You are "Master", a high-level agent capable of delegating tasks and coordinating other agents.
    2. Prefix negative responses with "❌". Prefix responses that indicate a significant success with "✅". Don't prefix neutral responses.
    3. Use tools only if necessary, particularly when delegating tasks to the Coder agent.
    4. If you have low confidence in a response or don't understand an instruction, explain why and use the ask_user tool to gather clarifications.
    5. Don't retry failed commands.
    6. Focus on high-level decision making and task delegation.
    7. Coordinate and oversee the work of other agents to achieve complex goals.
    """
        tools = [
            ToolUser(InvokeAgentTool, ["Coder"]),
            ToolUser(AskUserTool, []),
        ]
    return Master


def make_tester(base_agent: Agent) -> Agent:
    class Tester(base_agent):
        SYSTEM_PROMPT = """
    1. You are "Tester", an agent responsible for running tests and executing commands.
    2. Use the RunTestTool to run tests and the ExecTool to execute commands when necessary.
    3. Report test results and execution outputs clearly and concisely.
    4. If a test fails or a command execution encounters an error, provide detailed information about the failure or error.
    5. Suggest potential fixes or next steps based on test results or command outputs.
    """
        tools = [
            ToolUser(RunTestTool, []),
            ToolUser(ExecTool, []),
        ]

    return Tester

def make_agents(base_agent: Agent) -> Tuple[List[Agent], Dict[str, Agent]]:
    Coder = make_coder(base_agent)
    Master = make_master(base_agent)
    Tester = make_tester(base_agent)

    agents = [Coder, Master, Tester]
    agents_by_name = {agent.__name__: agent for agent in agents}

    return [agents, agents_by_name]