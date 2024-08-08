import {
// TODO    AskUserTool,
    CreateFileTool,
    DeleteFileTool,
// TODO    ExecTool,
    InvokeAgentTool,
    ReadFileTool,
    RenameFileTool,
// TODO    ReplaceInFileTool,
// TODO    RunTestTool,
    WriteFileTool,
// TODO    CAImportsTool,
// TODO    CAExportsTool,
// TODO    CAASTAnalyzerTool,
// TODO    CADependencyGraphTool,
} from "../tools";
import { CodeContext, getDefaultCodeContext } from "../code_context";
import { Agent } from "./agent";
import { loadEnvironment, getRootDir } from "../constants";
// TODO import { initialize_tracer, instrument } from "../instrumentation";
// TODO import { setup_logging } from "../util/logs";



export class EngineeringPlanner extends Agent {
    constructor() {
        super(
            "EngineeringPlanner",
            `
1. You are a planner agent.
2. You are responsible for converting high-level user tasks into much smaller and more specific engineering tasks for engineers to carry out.
3. You are also responsible for communicating with the user on interface design questions, whenever there are gaps.
4. You are always suspicious that requirements are incomplete.
5. You always try to find proof for requirement completeness before jumping to conclusions.
6. You are enthusiastic about working with the user on making sure that all requirements are understood and implemented.
7. When breaking down tasks, consider grouping related changes to minimize redundant work by the Coder.
`,
            [
                new InvokeAgentTool(["Engineer"]),
            ]
        )
    }
}


export class Engineer extends Agent {
    constructor() {
        super(
    "Engineer",
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
    [
        new InvokeAgentTool(["CodeAnalyst", "Coder", "Debugger"]),
    ]);
    }
}


export class CodeAnalyst extends Agent {
    constructor() {
        super(
            "CodeAnalyst",
            `
1. You are the CodeAnalyst agent, responsible for deep code analysis and understanding.
2. Use tools to provide comprehensive insights about the codebase.
3. Focus on identifying code locations that require changes or investigations, based on given requirements.
4. Provide detailed context and relationships between code elements.
5. Present your findings in a structured format that can be easily parsed and utilized by other agents.
`,
            [
                new ReadFileTool(),
                // TODO new CAImportsTool(),
                // TODO new CAExportsTool(),
                // TODO new CAASTAnalyzerTool(),
                // TODO new CADependencyGraphTool(),
            ]
        );

    }
}


export class Coder extends Agent {
    context: CodeContext;

    constructor() {
        super(
            "Coder",
            `
1. You are a programming agent who implements code changes based on very clear specifications.
2. You should only change the functions, classes or other code that have been specifically mentioned in the specs. Don't worry about changing anything else.
3. Use tools only if necessary.
4. Don't retry failed commands.
5. For simpler tasks, you have the autonomy to make decisions and implement changes without consulting other agents.
`,
            [
                new ReadFileTool(),
                new WriteFileTool(),
                new CreateFileTool(),
                new RenameFileTool(),
                new DeleteFileTool(),
                // TODO new ReplaceInFileTool(),
            ]
        );
    }

    initialize(): void {
        this.setContext(getDefaultCodeContext());
    }

    setContext(context: CodeContext): void {
        this.context = context;
    }

    preparePrompt(prompt: string): string {
        // TODO: known_files cost several hundred tokens for a small project.
        return `
These are all files: ${this.context.knownFiles}.
Query: ${prompt.trim()}
    `.trim();
    }

}


export class Debugger extends Agent {
    context: CodeContext;

    constructor() {
        super(
            "Debugger",
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
                new InvokeAgentTool(["Coder"]),
            ]
        );
    }

    initialize(): void {
        this.setContext(getDefaultCodeContext());
    }

    setContext(context: CodeContext): void {
        this.context = context;
    }

    preparePrompt(prompt: string): string {
        // TODO: known_files cost several hundred tokens for a small project.
        return `
These are all files: ${this.context.knownFiles}.
Query: ${prompt.trim()}
    `.trim()
    }
}


export class Manager extends Agent {
    context: CodeContext;

    constructor() {
        super(
            "Manager",
            `
1. You are the manager, a high-level agent capable of delegating tasks and coordinating other agents.
2. You do not read/write files or do any engineering work on your own.  Instead you delegate that work to other agents, and liase with the user, either through direct messages or through github PR comments.
2. Prefix negative responses with "❌". Prefix responses that indicate a significant success with "✅". Don't prefix neutral responses.
3. Use tools only if necessary.
4. Start by laying out a plan of all individual steps.
5. Make sure to finish all steps!
6. If you have low confidence in a response or don't understand an instruction, explain why and ask the user for clarification.
7. If the response from engineering is acceptable, relay it to the user.
`,
    [
        // new InvokeAgentTool(["EngineeringPlanner"]),
        new InvokeAgentTool(["Coder"]),
        // TODO new AskUserTool(),
    ]);
    }

    initialize(): void {
        this.setContext(getDefaultCodeContext());
    }

    setContext(context: CodeContext): void {
        this.context = context;
    }

    preparePrompt(prompt: string): string {
        // TODO: knownFiles cost several hundred tokens for a small project.
        return `
These are all files: ${this.context.knownFiles}.
Query: ${prompt.trim()}
    `.trim();
    }
}

type AgentConstructor = new () => Agent;
const agents = [Manager, EngineeringPlanner, CodeAnalyst, Coder, Debugger];
export const agentsByName: Record<string, AgentConstructor> = agents.reduce((acc, agent) => {
    acc[agent.name] = agent;
    return acc;
}, {});
