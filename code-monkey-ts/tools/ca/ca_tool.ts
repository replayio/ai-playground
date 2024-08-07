import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import { exec } from 'child_process';

const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);
const execAsync = promisify(exec);

interface CAResult {
    success: boolean;
    message: string;
    output?: string;
}

async function runCA(filePath: string, caCommand: string): Promise<CAResult> {
    try {
        const absolutePath = path.resolve(filePath);
        const command = `ca ${caCommand} "${absolutePath}"`;
        
        const { stdout, stderr } = await execAsync(command);
        
        if (stderr) {
            return {
                success: false,
                message: `Error: ${stderr}`,
            };
        }
        
        return {
            success: true,
            message: 'CA command executed successfully.',
            output: stdout.trim(),
        };
    } catch (error) {
        return {
            success: false,
            message: `Error: ${error.message}`,
        };
    }
}

export { runCA, CAResult };

// Main execution
if (require.main === module) {
    (async () => {
        if (process.argv.length !== 4) {
            console.error('Usage: node ca_tool.js <file_path> <ca_command>');
            process.exit(1);
        }

        const [, , filePath, caCommand] = process.argv;
        const result = await runCA(filePath, caCommand);
        console.log(result.message);
        if (result.output) {
            console.log('Output:', result.output);
        }
        process.exit(result.success ? 0 : 1);
    })();
}
