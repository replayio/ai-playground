import * as fs from 'fs';
import * as path from 'path';
import { tool } from "@langchain/core/tools";
import { z } from "zod";
import { makeFilePath } from './utils';
import { instrument } from '../instrumentation/instrument';
import { notifyFileModified } from './utils'; // Assuming this function exists in utils.ts

const schema = z.object({
    fname: z.string().describe("Name of the file to create."),
    content: z.string().optional().describe("Initial content of the file (optional)."),
});

export const createFileTool = tool(
    async ({ fname, content }: z.infer<typeof schema>) => {
        const filePath = makeFilePath(fname);
        
        try {
            await fs.promises.mkdir(path.dirname(filePath), { recursive: true });
            
            if (content !== undefined) {
                await fs.promises.writeFile(filePath, content, { flag: 'wx' });
            } else {
                await fs.promises.writeFile(filePath, '', { flag: 'wx' });
            }

            notifyFileModified(fname);
            return `File ${fname} created successfully.`;
        } catch (error) {
            console.error(`Failed to create file: ${filePath}`);
            console.error(error);
            throw error;
        }
    },
    {
        name: "create_file",
        description: "Create a new file with optional content",
        schema: schema,
    }
);

// Wrap the tool with instrumentation
export const instrumentedCreateFileTool = instrument(
    createFileTool,
    ['fname', 'content'],
    { tool: "CreateFileTool" }
);