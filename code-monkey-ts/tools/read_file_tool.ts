import * as fs from 'fs';
import { tool } from "@langchain/core/tools";
import { z } from "zod";
import { makeFilePath } from './utils';
import { instrument } from '../instrumentation/instrument';

const schema = z.object({
    fname: z.string().describe("The filename to read"),
});

export const readFileTool = tool(
    async ({ fname }: z.infer<typeof schema>) => {
        const filePath = makeFilePath(fname);
        try {
            const content = await fs.promises.readFile(filePath, 'utf8');
            return content;
        } catch (error) {
            console.error(`Failed to open file for reading: ${filePath}`);
            console.error(error);
            throw error;
        }
    },
    {
        name: "read_file",
        description: "Read the contents of the file of given name",
        schema: schema,
    }
);

// Wrapper function to apply instrumentation
const instrumentedReadFileTool = instrument(
    "Tool._run",
    ["fname"],
    { attributes: { tool: "ReadFileTool" } }
)(readFileTool);

export { instrumentedReadFileTool as readFileTool };