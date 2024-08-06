import * as fs from 'fs';
import * as path from 'path';
import { program } from 'commander';
import { Console } from 'console';
import { Manager } from './src/agents/agents';
import { getArtifactsDir, getRootDir } from './src/constants';
import { setupLogging } from './src/util/logs';

const console = new Console({ stdout: process.stdout, stderr: process.stderr });

class MainClass {
    static async main(debug: boolean = false): Promise<void> {
        setupLogging(debug);
        console.log("\x1b[1m\x1b[32mWelcome to the AI Playground!\x1b[0m");

        console.log("\x1b[1m\x1b[34mRunning Manager agent...\x1b[0m");

        const agent = new Manager("default");

        // Read prompt from .prompt.md file
        const promptPath = path.join(process.cwd(), ".prompt.md");
        const prompt = fs.readFileSync(promptPath, 'utf-8');

        await agent.runPrompt(prompt);
        console.log("\x1b[1m\x1b[32mDONE\x1b[0m");
    }
}

if (require.main === module) {
    program
        .option('--debug', 'Enable debug logging')
        .parse(process.argv);

    const options = program.opts();

    MainClass.main(options.debug)
        .then(() => process.exit(0))
        .catch((error) => {
            console.error(error);
            process.exit(1);
        });
}

export { MainClass as main };
