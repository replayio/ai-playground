import fs from 'fs';
import path from 'path';
import { z } from 'zod';
import { Tool } from '@langchain/core/tools';
import { CallbackManagerForToolRun } from '@langchain/core/callbacks/manager';
import { IOTool } from './ioTool';
import { makeFilePath } from './utils';
import { instrument } from '../instrumentation';

const CreateFileToolInputSchema = z.object({
  fname: z.string().describe("Name of the file to create."),
  content: z.string().optional().describe("Initial content of the file (optional).")
});

type CreateFileToolInput = z.infer<typeof CreateFileToolInputSchema>;

export class CreateFileTool extends IOTool {
  name = "create_file";
  description = "Create a new file with optional content";
  schema = CreateFileToolInputSchema;

  @instrument("Tool._run", ["fname", "content"], { attributes: { tool: "CreateFileTool" } })
  async _call(
    { fname, content }: CreateFileToolInput,
    runManager?: CallbackManagerForToolRun
  ): Promise<string> {
    const filePath = makeFilePath(fname);
    try {
      await fs.promises.mkdir(path.dirname(filePath), { recursive: true });
      await fs.promises.writeFile(filePath, content ?? '', { flag: 'wx' });
      this.notifyFileModified(fname);
      return `File ${fname} created successfully.`;
    } catch (error) {
      console.error(`Failed to create file: ${filePath}`);
      console.error(error);
      throw error;
    }
  }

  protected notifyFileModified(fname: string): void {
    // Implement the notification logic here
    console.log(`File ${fname} has been modified.`);
  }
}
