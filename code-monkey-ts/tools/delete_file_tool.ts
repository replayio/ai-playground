import * as fs from 'fs';
import { z } from "zod";
import { tool } from "@langchain/core/tools";
import { makeFilePath } from './utils';
import { instrument } from '../instrumentation';
import { notifyFileModified } from './io_tool';

const schema = z.object({
    fname: z.string().describe("Name of the file to delete.")
});

export const deleteFileTool = tool(
    async ({ fname }: z.infer<typeof schema>) => {
        const filePath = makeFilePath(fname);

        if (!fs.existsSync(filePath)) {
            throw new Error(`The file ${fname} does not exist.`);
        }

        fs.unlinkSync(filePath);
        notifyFileModified(fname);
        return null;
    },
    {
        name: "delete_file",
        description: "Delete a file by name",
        schema: schema,
    }
);

// Wrap the tool with instrumentation
export const instrumentedDeleteFileTool = instrument(
    deleteFileTool,
    "Tool._run",
    ["fname"],
    { attributes: { tool: "DeleteFileTool" } }
);