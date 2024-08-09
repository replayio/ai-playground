import * as fs from "fs";
import * as path from "path";
import { z } from "zod";
import { instrument, currentSpan } from "../instrumentation";
import { IOTool } from "./io_tool";
import { CodeContext } from "../code_context";

const schema = z.object({
  fname: z.string().describe("Name of the file to edit."),
  content: z.string().describe("New contents of the file."),
});

export class WriteFileTool extends IOTool {
  name = "write_file";
  description = "Write content to the file of given name";
  schema = schema;

  constructor(codeContext: CodeContext) {
    super(codeContext);
  }

  @instrument("Tool._call", { attributes: { tool: "WriteFileTool" } })
  async _call({ fname, content }: z.infer<typeof schema>): Promise<string> {
    currentSpan().setAttributes({
      fname: fname,
      content: content || "",
    });
    try {
      const filePath = this.codeContext.resolveFile(fname);
      fs.mkdirSync(path.dirname(filePath), { recursive: true });
      fs.writeFileSync(filePath, content);
      await this.notifyFileModified(fname);
      return "";
    } catch (error) {
      console.error(`Failed to write file: ${fname}`);
      console.error(error);
      return "failed to write file";
    }
  }
}