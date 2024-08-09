import * as fs from "fs";
import { z } from "zod";
import { instrument, currentSpan } from "../instrumentation";
import { IOTool } from "./io_tool";
import { CodeContext } from "../code_context";

const schema = z.object({
  fname: z.string().describe("Name of the file to delete."),
});

export class DeleteFileTool extends IOTool {
  name = "delete_file";
  description = "Delete a file by name";
  schema = schema;

  constructor(codeContext: CodeContext) {
    super(codeContext);
  }

  @instrument("Tool._call", { tool: "DeleteFileTool" })
  async _call({ fname }: z.infer<typeof schema>): Promise<string> {
    currentSpan().setAttributes({
      fname,
    });
    try {
      const filePath = this.codeContext.resolveFile(fname);
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