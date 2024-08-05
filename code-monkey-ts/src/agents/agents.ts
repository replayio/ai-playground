import { Agent } from './agent';
import { invokeAgent } from '../tools/invoke_agent_tool';
import { askUser } from '../tools/ask_user_tool';
import { instrument } from '../instrumentation/instrument';
import { CodeContext } from '../code_context';

class Manager extends Agent {
    static SYSTEM_PROMPT = `
    You are the Manager, an AI designed to manage and coordinate tasks among various agents.
    Your goal is to ensure that tasks are distributed efficiently and completed successfully.
    `;

    static tools = [
        invokeAgent,
        askUser,
    ];

    context: CodeContext;

    setContext(context: CodeContext): void {
        this.context = context;
    }

    preparePrompt(prompt: string): string {
        return `
        These are all files: ${this.context.copySrc()}.
        Query: ${prompt.trim()}
        `.trim();
    }
}

class EngineeringPlanner extends Agent {
    static SYSTEM_PROMPT = `
    You are the Engineering Planner, responsible for creating high-level plans for software projects.
    `;

    static tools = [askUser];
}

class Engineer extends Agent {
    static SYSTEM_PROMPT = `
    You are the Engineer, tasked with implementing technical solutions based on the plans provided.
    `;

    static tools = [askUser];
}

class CodeAnalyst extends Agent {
    static SYSTEM_PROMPT = `
    You are the Code Analyst, responsible for reviewing and analyzing code for quality and potential improvements.
    `;

    static tools = [askUser];
}

class Coder extends Agent {
    static SYSTEM_PROMPT = `
    You are the Coder, tasked with writing and modifying code based on specifications and requirements.
    `;

    static tools = [askUser];
}

class Debugger extends Agent {
    static SYSTEM_PROMPT = `
    You are the Debugger, responsible for identifying and fixing issues in the codebase.
    `;

    static tools = [askUser];
}

async function runAgentImpl(agentClass: typeof Agent): Promise<void> {
    const agent = new agentClass(null);
    await agent.runPrompt("");
}

async function runAgentMain(agentClass: typeof Agent): Promise<void> {
    await runAgentImpl(agentClass);
}

const agents: Array<typeof Agent> = [Manager, EngineeringPlanner, Engineer, CodeAnalyst, Coder, Debugger];

export { Manager, EngineeringPlanner, Engineer, CodeAnalyst, Coder, Debugger, runAgentMain, agents };
