import * as fs from "fs";
import * as path from "path";
import { z } from "zod";
import { makeFilePath } from "./utils";
import { instrument, currentSpan } from "../instrumentation";
import { IOTool } from "./io_tool";

const schema = z.object({
  fname: z.string().describe("Name of the file to create."),
  content: z
    .string()
    .optional()
    .describe("Initial content of the file (optional)."),
});

export class CreateFileTool extends IOTool {
  name = "create_file";
  description = "Create a new file with optional content";
  schema = schema;

  @instrument("Tool._call", { tool: "CreateFileTool" })
  async _call({ fname, content }: z.infer<typeof schema>): Promise<string> {
    currentSpan().setAttributes({
      fname,
      content: content || "",
    });
    try {
      const filePath = makeFilePath(fname);
      fs.mkdirSync(path.dirname(filePath), { recursive: true });
      fs.writeFileSync(filePath, content || "");
      await this.notifyFileModified(fname);
      return "file successfully created";
    } catch (error) {
      console.error(`Failed to create file: ${fname}`);
      console.error(error);
      return "failed to create file";
    }
  }
}
