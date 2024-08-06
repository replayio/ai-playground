import { promises as fs } from 'fs';
import * as path from 'path';
import { z } from 'zod';
import { CallbackManagerForToolRun } from '@langchain/core/callbacks/manager';
import { StructuredTool } from '@langchain/core/tools';
import { makeFilePath } from '../utils';
import { instrument } from '../../instrumentation';

const RenameFileToolInputSchema = z.object({
  oldName: z.string().describe("Current name of the file."),
  newName: z.string().describe("New name for the file.")
});

type RenameFileToolInput = z.infer<typeof RenameFileToolInputSchema>;

export const renameFileTool = new StructuredTool({
  name: "rename_file",
  description: "Rename a file, given old and new names",
  schema: RenameFileToolInputSchema,
  func: async (
    { oldName, newName }: RenameFileToolInput,
    runManager?: CallbackManagerForToolRun
  ): Promise<string> => {
    const oldPath = makeFilePath(oldName);
    const newPath = makeFilePath(newName);

    try {
      await fs.access(oldPath);
    } catch {
      throw new Error(`The file ${oldName} does not exist.`);
    }

    const newDir = path.dirname(newPath);
    await fs.mkdir(newDir, { recursive: true });

    try {
      await fs.access(newPath);
      throw new Error(`The file ${newName} already exists.`);
    } catch {
      // File does not exist, which is expected
    }

    await fs.rename(oldPath, newPath);
    return `File renamed from ${oldName} to ${newName}`;
  }
});

// Wrapper function to apply the instrumentation decorator
export const instrumentedRenameFileTool = instrument(
  "Tool.func",
  ["oldName", "newName"],
  { attributes: { tool: "RenameFileTool" } }
)(renameFileTool.func);

// You can use the instrumented version like this:
// renameFileTool.func = instrumentedRenameFileTool;
