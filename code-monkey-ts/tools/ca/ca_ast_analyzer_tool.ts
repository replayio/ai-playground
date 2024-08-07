import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import { exec } from 'child_process';

const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);
const execAsync = promisify(exec);

interface ASTAnalysisResult {
    success: boolean;
    message: string;
    output?: string;
}

async function analyzeAST(filePath: string): Promise<ASTAnalysisResult> {
    try {
        const absolutePath = path.resolve(filePath);
        const command = `ca ast "${absolutePath}"`;
        
        const { stdout, stderr } = await execAsync(command);
        
        if (stderr) {
            return {
                success: false,
                message: `Error: ${stderr}`,
            };
        }
        
        return {
            success: true,
            message: 'AST analysis completed successfully.',
            output: stdout.trim(),
        };
    } catch (error) {
        return {
            success: false,
            message: `Error: ${error.message}`,
        };
    }
}

export { analyzeAST, ASTAnalysisResult };

// Main execution
if (require.main === module) {
    (async () => {
        if (process.argv.length !== 3) {
            console.error('Usage: node ca_ast_analyzer_tool.js <file_path>');
            process.exit(1);
        }

        const [, , filePath] = process.argv;
        const result = await analyzeAST(filePath);
        console.log(result.message);
        if (result.output) {
            console.log('Output:', result.output);
        }
        process.exit(result.success ? 0 : 1);
    })();
}
