import * as fs from 'fs';
import * as path from 'path';
import { Console } from 'console';
import { TerminalMenu } from 'simple-term-menu';
import { Coder, CodeAnalyst, Manager } from './agents/agents';
import { loadEnvironment, getSrcDir } from './constants';
import { instrument, initializeTracer } from './instrumentation';
import { setupLogging } from './util/logs';

const console = new Console({ stdout: process.stdout, stderr: process.stderr });

@instrument('main')
async function main(debug: boolean = false): Promise<void> {
    setupLogging(debug);
    console.log('\x1b[1m\x1b[32mWelcome to the AI Agent Selector!\x1b[0m');

    const agentChoices: [string, typeof Coder | typeof CodeAnalyst | typeof Manager][] = [
        ['Coder', Coder],
        ['CodeAnalyst', CodeAnalyst],
        ['Manager', Manager],
    ];

    const menuItems = agentChoices.map((choice, index) => `${index + 1}. ${choice[0]}`);
    const terminalMenu = new TerminalMenu(menuItems, { title: 'Choose an agent to run:' });
    const menuEntryIndex = await terminalMenu.show();

    if (menuEntryIndex === undefined) {
        console.log('\x1b[1m\x1b[31mNo selection made. Exiting...\x1b[0m');
        return;
    }

    const [agentName, AgentClass] = agentChoices[menuEntryIndex];
    console.log(`\x1b[1m\x1b[34mRunning ${agentName} agent...\x1b[0m`);

    const agent = new AgentClass(process.env.AI_MSN);
    agent.initialize();

    // Read prompt from .prompt.md file
    const promptPath = path.join(getSrcDir(), '.prompt.md');
    const prompt = fs.readFileSync(promptPath, 'utf-8');

    await agent.runPrompt(prompt);
    console.log('\x1b[1m\x1b[32mDONE\x1b[0m');
}

if (require.main === module) {
    const args = process.argv.slice(2);
    const debug = args.includes('--debug');

    loadEnvironment();

    initializeTracer({
        agent: 'Coder',
    });

    main(debug).then(() => {
        process.exit(0);
    }).catch((error) => {
        console.error('An error occurred:', error);
        process.exit(1);
    });
}
