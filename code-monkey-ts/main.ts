import * as fs from 'fs';
import * as path from 'path';
import { Console } from 'console';
import chalk from 'chalk';
import { Coder, CodeAnalyst, Manager } from './agents/agents';
import { setupLogging } from './util/logs';

const console = new Console({ stdout: process.stdout, stderr: process.stderr });

type AgentType = 'Coder' | 'CodeAnalyst' | 'Manager';
type AgentClass = typeof Coder | typeof CodeAnalyst | typeof Manager;

async function main(debug: boolean = false): Promise<void> {
    setupLogging(debug);
    console.log(chalk.bold.green('Welcome to the AI Agent Selector!'));

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
            const _exhaustiveCheck: never = agentChoice;
            throw new Error(`Invalid agent choice: ${_exhaustiveCheck}`);
    }

    console.log(chalk.bold.blue(`Running ${agentChoice} agent...`));

    const agent = new AgentClass(process.env.AI_MSN || '');
    if ('initialize' in agent && typeof agent.initialize === 'function') {
        agent.initialize();
    }

    // Read prompt from .prompt.md file
    const promptPath = path.join(process.cwd(), '.prompt.md');
    const prompt = fs.readFileSync(promptPath, 'utf-8');

    await agent.runPrompt(prompt);
    console.log(chalk.bold.green('DONE'));
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