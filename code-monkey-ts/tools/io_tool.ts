import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import { exec } from 'child_process';

const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);
const execAsync = promisify(exec);

interface IOResult {
    success: boolean;
    output?: string;
    error?: string;
}

async function readFileContent(filePath: string): Promise<IOResult> {
    try {
        const content = await readFile(filePath, 'utf-8');
        return {
            success: true,
            output: content,
        };
    } catch (error) {
        return {
            success: false,
            error: error.message,
        };
    }
}

async function writeFileContent(filePath: string, content: string): Promise<IOResult> {
    try {
        await writeFile(filePath, content, 'utf-8');
        return {
            success: true,
            output: 'File written successfully.',
        };
    } catch (error) {
        return {
            success: false,
            error: error.message,
        };
    }
}

async function executeCommand(command: string): Promise<IOResult> {
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

export { readFileContent, writeFileContent, executeCommand, IOResult };

// Main execution
if (require.main === module) {
    console.log('This module provides I/O utility functions.');
    console.log('Import and use these functions in your TypeScript code as needed.');
}
