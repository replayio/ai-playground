import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import { exec } from 'child_process';

const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);
const execAsync = promisify(exec);

interface InvokeAgentResult {
    success: boolean;
    output?: string;
    error?: string;
}

async function invokeAgent(agentName: string, input: string): Promise<InvokeAgentResult> {
    try {
        // Write input to a temporary file
        const tempInputFile = path.join(__dirname, 'temp_input.txt');
        await writeFile(tempInputFile, input, 'utf8');

        // Execute the agent
        const command = `python -m code_monkey.main ${agentName} ${tempInputFile}`;
        const { stdout, stderr } = await execAsync(command);

        // Clean up temporary file
        fs.unlinkSync(tempInputFile);

        if (stderr) {
            return {
                success: false,
                error: stderr,
            };
        }

        return {
            success: true,
            output: stdout.trim(),
        };
    } catch (error) {
        return {
            success: false,
            error: error.message,
        };
    }
}

export { invokeAgent, InvokeAgentResult };

// Main execution
if (require.main === module) {
    (async () => {
        if (process.argv.length !== 4) {
            console.error('Usage: node invoke_agent_tool.js <agent_name> <input>');
            process.exit(1);
        }

        const [, , agentName, input] = process.argv;
        const result = await invokeAgent(agentName, input);

        if (result.success) {
            console.log('Agent output:');
            console.log(result.output);
        } else {
            console.error('Error:', result.error);
        }

        process.exit(result.success ? 0 : 1);
    })();
}
