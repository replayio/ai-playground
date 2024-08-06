import * as fs from 'fs';
import * as path from 'path';
import { Console } from 'console';
import { Coder, CodeAnalyst, Manager } from './agents/agents';
import { getArtifactsDir } from './constants';
import { setupLogging } from './util/logs';

const console = new Console({ stdout: process.stdout, stderr: process.stderr });

type AgentType = 'Coder' | 'CodeAnalyst' | 'Manager';
type AgentClass = typeof Coder | typeof CodeAnalyst | typeof Manager;

async function main(debug: boolean = false): Promise<void> {
    setupLogging(debug);
    console.log('\x1b[1m\x1b[32mWelcome to the AI Agent Selector!\x1b[0m');

    console.log('Available agents:');
    console.log('1. Coder');
    console.log('2. CodeAnalyst');
    console.log('3. Manager');

    const agentChoice = 'Manager' as AgentType; // For now, we'll default to the Manager agent
    let AgentClass: AgentClass;

    switch (agentChoice) {
        case 'Coder':
            AgentClass = Coder;
            break;
        case 'CodeAnalyst':
            AgentClass = CodeAnalyst;
            break;
        case 'Manager':
            AgentClass = Manager;
            break;
        default:
            throw new Error(`Invalid agent choice: ${agentChoice satisfies never}`);
    }

    console.log(`\x1b[1m\x1b[34mRunning ${agentChoice} agent...\x1b[0m`);

    const agent = new AgentClass(process.env.AI_MSN || '');
    if ('initialize' in agent && typeof agent.initialize === 'function') {
        agent.initialize();
    }

    // Read prompt from .prompt.md file
    const promptPath = path.join(process.cwd(), '.prompt.md');
    const prompt = fs.readFileSync(promptPath, 'utf-8');

    await agent.runPrompt(prompt);
    console.log('\x1b[1m\x1b[32mDONE\x1b[0m');
}

if (require.main === module) {
    const args = process.argv.slice(2);
    const debug = args.includes('--debug');

    main(debug).then(() => {
        process.exit(0);
    }).catch((error) => {
        console.error('An error occurred:', error);
        process.exit(1);
    });
}
