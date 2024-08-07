import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import { exec } from 'child_process';
import { tool } from "@langchain/core/tools";
import { z } from "zod";
import { CustomEvent } from "@langchain/core/callbacks/manager";

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

const notifyFileModified = (filePath: string) => {
    const event: CustomEvent = {
        name: "file_modified",
        data: filePath,
    };
    // Note: You'll need to implement or import a function to dispatch custom events
    // For example: dispatchCustomEvent(event);
    console.log("Custom event dispatched:", event);
};

const schema = z.object({
    filePath: z.string().describe("The path of the modified file"),
});

export const ioTool = tool(
    async ({ filePath }: z.infer<typeof schema>) => {
        notifyFileModified(filePath);
        return `Notified that file ${filePath} was modified`;
    },
    {
        name: "io_tool",
        description: "Notify when a file has been modified",
        schema: schema,
    }
);

export { readFileContent, writeFileContent, executeCommand, IOResult };

// Main execution
if (require.main === module) {
    console.log('This module provides I/O utility functions and tools.');
    console.log('Import and use these functions and tools in your TypeScript code as needed.');
}