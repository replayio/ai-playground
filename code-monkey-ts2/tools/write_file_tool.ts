import * as fs from 'fs';
import * as path from 'path';
import { z } from "zod";
import { makeFilePath } from './utils';
import { instrument, currentSpan } from '../instrumentation';
import { IOTool } from './io_tool';

const schema = z.object({
    fname: z.string().describe("Name of the file to edit."),
    content: z.string().describe("New contents of the file."),
});

export class WriteFileTool extends IOTool {
    name = "write_file";
    description = "Write content to the file of given name";
    schema = schema;


    @instrument("Tool._call", { tool: "WriteFileTool" })
    async _call({ fname, content }: z.infer<typeof schema>): Promise<string> {
        currentSpan().setAttributes({
            fname: fname,
            content: content || ""
        });
        try {
            const filePath = makeFilePath(fname);
            fs.mkdirSync(path.dirname(filePath), { recursive: true });
            fs.writeFileSync(filePath, content);
            await this.notifyFileModified(fname);
            return "file successfully written";
        } catch (error) {
            console.error(`Failed to write file: ${fname}`);
            console.error(error);
            return "failed to write file";
        }
    }
}