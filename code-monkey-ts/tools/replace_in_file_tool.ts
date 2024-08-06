import { z } from 'zod';
import { AsyncCallbackManagerForToolRun } from '@langchain/core/callbacks/manager';
import { tool } from '@langchain/core/tools';
import { IOTool } from './io_tool';
import { makeFilePath } from './utils';
import { instrument } from '../instrumentation';

const ReplaceInFileToolInputSchema = z.object({
    fname: z.string().describe("Name of the file to edit."),
    to_replace: z.string().describe("The string to be replaced."),
    replacement: z.string().describe("The string to replace with.")
});

type ReplaceInFileToolInput = z.infer<typeof ReplaceInFileToolInputSchema>;

export class ReplaceInFileTool extends IOTool {
    name = "replace_in_file";
    description = "Replace a specific string in a file with another string";
    schema = ReplaceInFileToolInputSchema;

    @instrument(
        "Tool._run",
        ["fname", "to_replace", "replacement"],
        { attributes: { tool: "ReplaceInFileTool" } }
    )
    async _run(
        { fname, to_replace, replacement }: ReplaceInFileToolInput,
        runManager?: AsyncCallbackManagerForToolRun
    ): Promise<void> {
        const filePath = makeFilePath(fname);
        const content = await fs.promises.readFile(filePath, 'utf-8');

        const occurrences = (content.match(new RegExp(to_replace, 'g')) || []).length;
        if (occurrences !== 1) {
            throw new Error(
                `The string '${to_replace}' appears ${occurrences} times in the file. It must appear exactly once for replacement.`
            );
        }

        const newContent = content.replace(to_replace, replacement);

        await fs.promises.writeFile(filePath, newContent, 'utf-8');

        this.notifyFileModified(fname);
    }
}

export const replaceInFileTool = tool({
    name: "replace_in_file",
    description: "Replace a specific string in a file with another string",
    schema: ReplaceInFileToolInputSchema,
    func: async (input: ReplaceInFileToolInput, runManager?: AsyncCallbackManagerForToolRun) => {
        const tool = new ReplaceInFileTool();
        await tool._run(input, runManager);
    }
});
