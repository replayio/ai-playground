import * as fs from 'fs';
import * as path from 'path';
import { z } from 'zod';
import { CallbackManagerForToolRun } from '@langchain/core/callbacks/manager';
import { tool } from '@langchain/core/tools';
import { makeFilePath } from '../utils';
import { instrument } from '../../instrumentation';

const WriteFileToolInputSchema = z.object({
  fname: z.string().describe("Name of the file to edit."),
  content: z.string().describe("New contents of the file.")
});

type WriteFileToolInput = z.infer<typeof WriteFileToolInputSchema>;

export const writeFileTool = tool({
  name: "write_file",
  description: "Write content to the file of given name",
  schema: WriteFileToolInputSchema,
  func: async (
    { fname, content }: WriteFileToolInput,
    runManager?: CallbackManagerForToolRun
  ): Promise<string> => {
    const filePath = makeFilePath(fname);
    try {
      await fs.promises.mkdir(path.dirname(filePath), { recursive: true });
      await fs.promises.writeFile(filePath, content);
      notifyFileModified(fname);
      return `File ${fname} has been written successfully.`;
    } catch (error) {
      console.error(`Failed to write file: ${filePath}`);
      console.error(error);
      throw error;
    }
  }
});

function notifyFileModified(fname: string): void {
  // Implement file modification notification logic here
  console.log(`File modified: ${fname}`);
}

// Wrapper function to apply the instrumentation decorator
export const instrumentedWriteFileTool = instrument(
  "Tool.func",
  ["fname", "content"],
  { attributes: { tool: "WriteFileTool" } }
)(writeFileTool.func);

// You can use the instrumented version like this:
// writeFileTool.func = instrumentedWriteFileTool;

// Simple test case
if (require.main === module) {
  (async () => {
    const testFileName = 'test_write_file.txt';
    const testContent = 'This is a test content.';
    try {
      const result = await writeFileTool.func({ fname: testFileName, content: testContent });
      console.log(result);
      const fileContent = await fs.promises.readFile(makeFilePath(testFileName), 'utf-8');
      if (fileContent === testContent) {
        console.log('Test passed: File content matches the input.');
      } else {
        console.error('Test failed: File content does not match the input.');
      }
      await fs.promises.unlink(makeFilePath(testFileName));
    } catch (error) {
      console.error('Test failed:', error);
    }
  })();
}
