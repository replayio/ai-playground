import * as fs from 'fs';
import * as path from 'path';
import { Tool } from 'langchain/tools';
import { CallbackManagerForToolRun } from 'langchain/callbacks';
import { makeFilePath } from './utils';
import { instrument } from '../instrumentation';

export interface ReadFileToolInput {
    fname: string;
}

export class ReadFileTool extends Tool {
    name = "read_file";
    description = "Read the contents of the file of given name";

    constructor() {
        super({
            name: this.name,
            description: this.description,
        });
    }

    @instrument("Tool._run", ["fname"], { attributes: { tool: "ReadFileTool" } })
    async _call(
        input: ReadFileToolInput,
        runManager?: CallbackManagerForToolRun
    ): Promise<string> {
        const filePath: string = makeFilePath(input.fname);
        try {
            const content: string = await fs.promises.readFile(filePath, 'utf-8');
            return content;
        } catch (error) {
            console.error(`Failed to open file for reading: ${filePath}`);
            console.error(error);
            // Re-throw the error
            throw error;
        }
    }
}
