import * as fs from 'fs';
import * as path from 'path';
import { tool } from "@langchain/core/tools";
import { z } from "zod";
import { makeFilePath } from './utils';
import { instrument } from '../instrumentation/instrument';
import { notifyFileModified } from './utils'; // Assuming this function exists in utils.ts

const schema = z.object({
    fname: z.string().describe("Name of the file to edit."),
    content: z.string().describe("New contents of the file."),
});

export const writeFileTool = tool(
    instrument("Tool._run", ["fname", "content"], { tool: "WriteFileTool" })(
        async ({ fname, content }: z.infer<typeof schema>) => {
            const filePath = makeFilePath(fname);
            try {
                fs.mkdirSync(path.dirname(filePath), { recursive: true });
                fs.writeFileSync(filePath, content);
                notifyFileModified(fname);
                return null;
            } catch (error) {
                console.error(`Failed to write file: ${filePath}`);
                console.error(error);
                throw error;
            }
        }
    ),
    {
        name: "write_file",
        description: "Write content to the file of given name",
        schema: schema,
    }
);