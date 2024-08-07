import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const writeFile = promisify(fs.writeFile);

interface WriteFileResult {
    success: boolean;
    message: string;
}

async function writeFileImpl(filePath: string, content: string): Promise<WriteFileResult> {
    try {
        const absolutePath = path.resolve(filePath);
        await writeFile(absolutePath, content, 'utf8');
        return {
            success: true,
            message: 'File written successfully.',
        };
    } catch (error) {
        return {
            success: false,
            message: `Error: ${error.message}`,
        };
    }
}

const schema = z.object({
    filePath: z.string().describe("The path to the file to write"),
    content: z.string().describe("The content to write to the file")
});

export const writeFileTool = tool(
    async ({ filePath, content }: z.infer<typeof schema>) => {
        const result = await writeFileImpl(filePath, content);
        return JSON.stringify(result);
    },
    {
        name: "write_file",
        description: "Write content to a file at the specified path",
        schema: schema,
    }
);

// Main execution
if (require.main === module) {
    (async () => {
        if (process.argv.length !== 4) {
            console.error('Usage: node write_file_tool.js <file_path> <content>');
            process.exit(1);
        }

        const [, , filePath, content] = process.argv;
        const result = await writeFileImpl(filePath, content);
        console.log(result.message);
        process.exit(result.success ? 0 : 1);
    })();
}