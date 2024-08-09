import { z } from "zod";
import { readFileContent } from "./utils";
import { instrument, currentSpan } from "../instrumentation";
import { IOTool } from './io_tool';
import { CodeContext } from "../code_context";

const schema = z.object({
  fname: z.string().describe("Name of the file to edit."),
});

export class ReadFileTool extends IOTool {
  name = "read_file";
  description =
    "Read the contents of the file of given name.";
  schema = schema;

  constructor(codeContext: CodeContext) {
    super(codeContext);
  }

  @instrument("Tool._call", { tool: "ReadFileTool" })
  async _call({ fname }: z.infer<typeof schema>): Promise<string> {
    currentSpan().setAttributes({
      fname,
    });
    const filePath = this.codeContext.resolveFile(fname);
    try {
      const content = await readFileContent(filePath);
      return `${content}`;
    } catch (error) {
      // console.error(`Failed to open file for reading: ${filePath}`);
      // console.error(error);
      return `Failed to read file: ${error?.stack || error}`;
    }
  }
}