from agent import ClaudeAgent, ToolUser
from tools.invoke_agent_tool import InvokeAgentTool
from tools.read_file_tool import ReadFileTool
from tools.write_file_tool import WriteFileTool
from tools.list_files_tool import ListFilesTool
from tools.io_tool import IOTool


class Coder(ClaudeAgent):
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
        ToolUser(ListFilesTool, []),
        ToolUser(IOTool, []),
    ]


class Master(ClaudeAgent):
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
        ToolUser(InvokeAgentTool, [["Coder"]])
    ]


agents = [Coder, Master]
agents_by_name = {agent.__name__: agent for agent in agents}