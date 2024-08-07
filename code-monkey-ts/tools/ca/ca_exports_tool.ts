import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import { exec } from 'child_process';

const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);
const execAsync = promisify(exec);

interface ExportResult {
    success: boolean;
    message: string;
    output?: string;
}

async function addExport(filePath: string, exportStatement: string): Promise<ExportResult> {
    try {
        const absolutePath = path.resolve(filePath);
        let fileContent = await readFile(absolutePath, 'utf8');

        // Check if the export already exists
        if (fileContent.includes(exportStatement)) {
            return {
                success: false,
                message: 'Export already exists in the file.',
            };
        }

        // Add the export statement at the end of the file
        fileContent += '\n' + exportStatement + '\n';

        await writeFile(absolutePath, fileContent, 'utf8');
        return {
            success: true,
            message: 'Export added successfully.',
        };
    } catch (error) {
        return {
            success: false,
            message: `Error: ${error.message}`,
        };
    }
}

async function runCAExports(filePath: string): Promise<ExportResult> {
    try {
        const absolutePath = path.resolve(filePath);
        const command = `ca exports "${absolutePath}"`;
        
        const { stdout, stderr } = await execAsync(command);
        
        if (stderr) {
            return {
                success: false,
                message: `Error: ${stderr}`,
            };
        }
        
        return {
            success: true,
            message: 'CA exports command executed successfully.',
            output: stdout.trim(),
        };
    } catch (error) {
        return {
            success: false,
            message: `Error: ${error.message}`,
        };
    }
}

export { addExport, runCAExports, ExportResult };

// Main execution
if (require.main === module) {
    (async () => {
        if (process.argv.length < 3 || process.argv.length > 4) {
            console.error('Usage: node ca_exports_tool.js <file_path> [export_statement]');
            process.exit(1);
        }

        const [, , filePath, exportStatement] = process.argv;
        
        if (exportStatement) {
            const result = await addExport(filePath, exportStatement);
            console.log(result.message);
        } else {
            const result = await runCAExports(filePath);
            console.log(result.message);
            if (result.output) {
                console.log('Output:', result.output);
            }
        }
        
        process.exit(result.success ? 0 : 1);
    })();
}
