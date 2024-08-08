import * as fs from 'fs';
import * as path from 'path';
import { StructuredTool, tool, Tool, ToolParams } from "@langchain/core/tools";
import { z } from "zod";
import { makeFilePath, readFileContent } from './utils';
// TODO import { instrument } from '../instrumentation';

const schema = z.object({
    fname: z.string().describe("Name of the file to edit."),
});

export class ReadFileTool extends StructuredTool {
    name = "read_file"
    description = "Read the contents of the file of given name.  can be used as a way to check for file existence."
    schema = schema;

    // TODO @instrument("Tool._call", ["fname"], { tool: "ReadFileTool" })
    async _call({ fname }: z.infer<typeof schema>): Promise<string> {
        console.log(`Reading file: ${fname}`);
        const filePath = makeFilePath(fname);
        try {
            const content = await readFileContent(filePath);
            return `File content: ${content}`;
        } catch (error) {
            // console.error(`Failed to open file for reading: ${filePath}`);
            // console.error(error);
            return "Failed to read file";
        }
    }
}