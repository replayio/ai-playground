import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

interface RunTestResult {
    success: boolean;
    output?: string;
    error?: string;
}

async function runTestTool(testCommand: string): Promise<RunTestResult> {
    try {
        const { stdout, stderr } = await execAsync(testCommand);
        return {
            success: true,
            output: stdout.trim(),
            error: stderr.trim(),
        };
    } catch (error) {
        return {
            success: false,
            error: error.message,
        };
    }
}

export { runTestTool, RunTestResult };

// Main execution
if (require.main === module) {
    (async () => {
        if (process.argv.length < 3) {
            console.error('Usage: node run_test_tool.js <test_command>');
            process.exit(1);
        }

        const testCommand = process.argv.slice(2).join(' ');
        const result = await runTestTool(testCommand);
        
        if (result.success) {
            console.log('Test output:');
            console.log(result.output);
            if (result.error) {
                console.error('Test errors:');
                console.error(result.error);
            }
        } else {
            console.error('Test execution failed:');
            console.error(result.error);
        }
        
        process.exit(result.success ? 0 : 1);
    })();
}
