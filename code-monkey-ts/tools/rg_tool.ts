import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

interface RgResult {
    success: boolean;
    output?: string;
    error?: string;
}

async function runRipgrep(pattern: string, path: string, flags: string[] = []): Promise<RgResult> {
    const command = `rg ${flags.join(' ')} "${pattern}" "${path}"`;
    
    try {
        const { stdout, stderr } = await execAsync(command);
        return {
            success: true,
            output: stdout.trim(),
        };
    } catch (error) {
        if (error.code === 1 && !error.stderr) {
            // No matches found, but command executed successfully
            return {
                success: true,
                output: '',
            };
        }
        return {
            success: false,
            error: error.message,
        };
    }
}

export { runRipgrep, RgResult };

// Main execution
if (require.main === module) {
    (async () => {
        if (process.argv.length < 4) {
            console.error('Usage: node rg_tool.js <pattern> <path> [flags...]');
            process.exit(1);
        }

        const [, , pattern, path, ...flags] = process.argv;
        const result = await runRipgrep(pattern, path, flags);
        
        if (result.success) {
            console.log(result.output);
        } else {
            console.error(result.error);
        }
        
        process.exit(result.success ? 0 : 1);
    })();
}
