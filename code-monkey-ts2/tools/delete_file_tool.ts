import * as fs from 'fs';
import * as path from 'path';
import { z } from "zod";
import { makeFilePath } from './utils';
// TODO import { instrument } from '../instrumentation';
import { IOTool } from './io_tool';

const schema = z.object({
    fname: z.string().describe("Name of the file to delete."),
});

export class DeleteFileTool extends IOTool {
    name = "delete_file";
    description = "Delete a file by name";
    schema = schema;


    // TODO @instrument("Tool._call", ["fname", "content"], { tool: "DeleteFileTool" })
    async _call({ fname }: z.infer<typeof schema>): Promise<string> {
        try {
            const filePath = makeFilePath(fname);
            fs.unlinkSync(filePath);
            await this.notifyFileModified(fname);
            return "file successfully deleted";
        } catch (error) {
            console.error(`Failed to delete file: ${fname}`);
            console.error(error);
            return "failed to delete file";
        }
    }
}