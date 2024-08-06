import { promises as fs } from 'fs';
import { z } from 'zod';
import { tool } from '@langchain/core/tools';
import { CallbackManagerForToolRun } from '@langchain/core/callbacks/manager';
import { makeFilePath } from './utils';
import { instrument } from '../instrumentation';

const ReadFileToolInputSchema = z.object({
  fname: z.string().describe("The name of the file to read")
});

type ReadFileToolInput = z.infer<typeof ReadFileToolInputSchema>;

export const readFileTool = tool({
  name: "read_file",
  description: "Read the contents of the file of given name",
  schema: ReadFileToolInputSchema,
  func: async (
    { fname }: ReadFileToolInput,
    runManager?: CallbackManagerForToolRun
  ): Promise<string> => {
    const filePath: string = makeFilePath(fname);
    try {
      const content: string = await fs.readFile(filePath, 'utf-8');
      return content;
    } catch (error) {
      console.error(`Failed to open file for reading: ${filePath}`);
      console.error(error);
      // Re-throw the error
      throw error;
    }
  }
});

// Wrapper function to apply the instrumentation decorator
export const instrumentedReadFileTool = instrument(
  "Tool.func",
  ["fname"],
  { attributes: { tool: "ReadFileTool" } }
)(readFileTool.func);

// You can use the instrumented version like this:
// readFileTool.func = instrumentedReadFileTool;
