import {
  // TODO    AskUserTool,
  CreateFileTool,
  DeleteFileTool,
  // TODO    ExecTool,
  InvokeAgentTool,
  ReadFileTool,
  RenameFileTool,
  ReplaceInFileTool,
  // TODO    RunTestTool,
  WriteFileTool,
  // TODO    CAImportsTool,
  // TODO    CAExportsTool,
  // TODO    CAASTAnalyzerTool,
  // TODO    CADependencyGraphTool,
} from "../tools";
import { CodeContext } from "../code_context";
import { Agent, AgentConstructor } from "./agent";

export class EngineeringPlanner extends Agent {
  constructor(codeContext: CodeContext) {
    super(
      `
1. You are a planner agent.
2. You are responsible for converting high-level user tasks into much smaller and more specific engineering tasks for engineers to carry out.
3. You are also responsible for communicating with the user on interface design questions, whenever there are gaps.
4. You are always suspicious that requirements are incomplete.
5. You always try to find proof for requirement completeness before jumping to conclusions.
6. You are enthusiastic about working with the user on making sure that all requirements are understood and implemented.
7. When breaking down tasks, consider grouping related changes to minimize redundant work by the Coder.
`,
      [new InvokeAgentTool(["Engineer"], codeContext)],
      codeContext
    );
  }
}

export class Engineer extends Agent {
  constructor(codeContext: CodeContext) {
    super(
      `
1. You are an engineering brain.
2. Take on one engineering task at a time. Each task should be limited to specific code locations.
3. Delegate the actual coding to the coder agent.
4. Delegate testing or running of programs to a debugger agent.
5. When you receive reports from coder and debugger agents, you determine whether your job is done or whether more work is required.
6. Upon reviewing reports you check for task completeness. As long as there are more obvious tasks, you ask the CodeAnalyst agent to find relevant code locations, and then ask the coder to change them, and/or the debugger to test them.
7. TODO: Implement a mechanism to subdivide engineering tasks into smaller tasks upon discovery.
8. Provide clear and detailed instructions to the Coder agent to minimize the need for clarifications.
`,
      [new InvokeAgentTool(["CodeAnalyst", "Coder", "Debugger"], codeContext)],
      codeContext
    );
  }
}

export class CodeAnalyst extends Agent {
  constructor(codeContext: CodeContext) {
    super(
      `
1. You are the CodeAnalyst agent, responsible for deep code analysis and understanding.
2. Use tools to provide comprehensive insights about the codebase.
3. Focus on identifying code locations that require changes or investigations, based on given requirements.
4. Provide detailed context and relationships between code elements.
5. Present your findings in a structured format that can be easily parsed and utilized by other agents.
`,
      [
        new ReadFileTool(codeContext),
        // TODO new CAImportsTool(),
        // TODO new CAExportsTool(),
        // TODO new CAASTAnalyzerTool(),
        // TODO new CADependencyGraphTool()
      ],
      codeContext
    );
  }
}

export class Coder extends Agent {
  constructor(codeContext: CodeContext) {
    super(
      `
1. You are a programming agent who implements code changes based on very clear specifications.
2. You should only change the functions, classes or other code that have been specifically mentioned in the specs. Don't worry about changing anything else.
3. Use tools only if necessary.
4. Don't retry failed commands.
5. Keep your responses VERY brief. Only provide VERY SHORT summaries of your changes. Don't respond with code.
`,
      [
        new ReadFileTool(codeContext),
        new WriteFileTool(codeContext),
        new CreateFileTool(codeContext),
        new RenameFileTool(codeContext),
        new DeleteFileTool(codeContext),
        new ReplaceInFileTool(codeContext),
      ],
      codeContext
    );
  }
}

export class Debugger extends Agent {
  constructor(codeContext: CodeContext) {
    super(
      `
1. You are "Tester", an agent responsible for running tests and executing commands.
2. Use the RunTestTool to run tests and the ExecTool to execute commands when necessary.
3. Report test results and execution outputs clearly and concisely.
4. If a test fails or a command execution encounters an error, provide detailed information about the failure or error.
5. Suggest potential fixes or next steps based on test results or command outputs.
6. Provide feedback to the Coder agent on common issues or patterns observed during testing to help improve code quality.
`,
      [
        // TODO new RunTestTool(),
        // TODO new ExecTool(),
        new InvokeAgentTool(["Coder"], codeContext),
      ],
      codeContext
    );
  }
}

export class Manager extends Agent {
  constructor(codeContext: CodeContext) {
    super(
      `
1. You are the manager, a high-level agent capable of delegating tasks and coordinating other agents.
2. You do not read/write files or do any engineering work on your own.  Instead you delegate that work to other agents.
3. Prefix negative responses with "❌". Prefix responses that indicate a significant success with "✅". Don't prefix neutral responses.
4. Start by laying out a plan of individual steps.
5. Keep the task you assign to any agent as small as possible.
6. Keep instructions and responses brief. Always focus on one problem at a time.
`,
      // 6. Make sure to finish all steps.
      [
        // new InvokeAgentTool(["EngineeringPlanner"],codeContext),
        new InvokeAgentTool(["Coder"], codeContext),
        // TODO new AskUserTool(),
      ],
      codeContext
    );
  }
}

const agentsByName = new Map<string, AgentConstructor>();
registerAgents([Manager, EngineeringPlanner, CodeAnalyst, Coder, Debugger]);

export function registerAgents(As: AgentConstructor[]): void {
  As.forEach((A) => {
    registerAgent(A);
  });
}

export function registerAgent(A: AgentConstructor): void {
  if (agentsByName.has(A.name)) {
    throw new Error(`Agent already registered: ${A.name}`);
  }
  agentsByName.set(A.name, A);
}

export function getAgentByName(name: string): AgentConstructor {
  const A = agentsByName.get(name);
  if (!A) {
    throw new Error(`Agent not found: ${name}`);
  }
  return A;
}
