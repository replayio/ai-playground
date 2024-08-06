import { Agent } from './agent';
import { InvokeAgentTool } from '../tools/invoke_agent_tool';
import { AskUserTool } from '../tools/ask_user_tool';
import { instrument } from '../instrumentation/instrument';
import { CodeContext } from '../code_context';
import { Tool } from '@langchain/core/tools';

class Manager extends Agent {
    static override SYSTEM_PROMPT = `
    You are the Manager, an AI designed to manage and coordinate tasks among various agents.
    Your goal is to ensure that tasks are distributed efficiently and completed successfully.
    `;

    static override tools: Tool[] = [
        new InvokeAgentTool() as unknown as Tool,
        new AskUserTool() as unknown as Tool,
    ];

    context: CodeContext;

    constructor(msn: string) {
        super(msn);
        this.context = new CodeContext();
    }

    setContext(context: CodeContext): void {
        this.context = context;
    }

    override preparePrompt(prompt: string): string {
        return `
        These are all files: ${this.context.copySrc()}.
        Query: ${prompt.trim()}
        `.trim();
    }
}

class EngineeringPlanner extends Agent {
    static override SYSTEM_PROMPT = `
    You are the Engineering Planner, responsible for creating high-level plans for software projects.
    `;

    static override tools: Tool[] = [new AskUserTool() as unknown as Tool];
}

class Engineer extends Agent {
    static override SYSTEM_PROMPT = `
    You are the Engineer, tasked with implementing technical solutions based on the plans provided.
    `;

    static override tools: Tool[] = [new AskUserTool() as unknown as Tool];
}

class CodeAnalyst extends Agent {
    static override SYSTEM_PROMPT = `
    You are the Code Analyst, responsible for reviewing and analyzing code for quality and potential improvements.
    `;

    static override tools: Tool[] = [new AskUserTool() as unknown as Tool];
}

class Coder extends Agent {
    static override SYSTEM_PROMPT = `
    You are the Coder, tasked with writing and modifying code based on specifications and requirements.
    `;

    static override tools: Tool[] = [new AskUserTool() as unknown as Tool];
}

class Debugger extends Agent {
    static override SYSTEM_PROMPT = `
    You are the Debugger, responsible for identifying and fixing issues in the codebase.
    `;

    static override tools: Tool[] = [new AskUserTool() as unknown as Tool];
}

async function runAgentImpl(agentClass: new (msn: string) => Agent): Promise<void> {
    const agent = new agentClass("default");
    await agent.runPrompt("");
}

async function runAgentMain(agentClass: new (msn: string) => Agent): Promise<void> {
    await runAgentImpl(agentClass);
}

const agents: Array<new (msn: string) => Agent> = [Manager, EngineeringPlanner, Engineer, CodeAnalyst, Coder, Debugger];

export { Manager, EngineeringPlanner, Engineer, CodeAnalyst, Coder, Debugger, runAgentMain, agents };
