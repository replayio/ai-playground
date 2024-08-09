import * as fs from "fs";
import { z } from "zod";
import { instrument, currentSpan } from "../instrumentation";
import { IOTool } from "./io_tool";
import { CodeContext } from "../code_context";

const schema = z.object({
  old_name: z.string().describe("Current name of the file."),
  new_name: z.string().describe("New name for the file."),
});

export class RenameFileTool extends IOTool {
  name = "rename_file";
  description = "Rename a file, given old and new names";
  schema = schema;

  constructor(codeContext: CodeContext) {
    super(codeContext);
  }

  @instrument("Tool._call", { tool: "RenameFileTool" })
  async _call({ old_name, new_name }: z.infer<typeof schema>): Promise<string> {
    currentSpan().setAttributes({
      old_name,
      new_name,
    });

    try {
      const oldPath = this.codeContext.resolveFile(old_name);
      const newPath = this.codeContext.resolveFile(new_name);

      fs.renameSync(oldPath, newPath);

      await this.notifyFileModified(old_name);
      await this.notifyFileModified(new_name);
      return "file successfully renamed";
    } catch (error) {
      console.error(`Failed to rename file: ${old_name} to ${new_name}`);
      console.error(error);
      return "failed to rename file";
    }
  }
}