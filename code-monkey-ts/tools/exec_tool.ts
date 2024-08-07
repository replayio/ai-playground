import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import { exec } from 'child_process';

const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);
const execAsync = promisify(exec);

interface ExecToolResult {
    success: boolean;
    output?: string;
    error?: string;
}

async function execTool(command: string): Promise<ExecToolResult> {
    try {
        const { stdout, stderr } = await execAsync(command);

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

export { execTool, ExecToolResult };

// Main execution
if (require.main === module) {
    (async () => {
        if (process.argv.length !== 3) {
            console.error('Usage: node exec_tool.js <command>');
            process.exit(1);
        }

        const [, , command] = process.argv;
        const result = await execTool(command);

        if (result.success) {
            console.log('Command output:');
            console.log(result.output);
        } else {
            console.error('Error:', result.error);
        }

        process.exit(result.success ? 0 : 1);
    })();
}
