import { z } from "zod";
import { readFileContent, writeFileContent } from "./utils";
import { instrument, currentSpan } from "../instrumentation";
import { IOTool } from "./io_tool";
import { CodeContext } from "../code_context";

const schema = z.object({
  fname: z.string().describe("The path to the file to be modified."),
  oldText: z.string().describe("The text to be replaced."),
  newText: z.string().describe("The text to replace with."),
});

export class ReplaceInFileTool extends IOTool {
  name = "replace_in_file";
  description =
    "Replace all occurrences of given text in a file with the replacement";
  schema = schema;

  constructor(codeContext: CodeContext) {
    super(codeContext);
  }

  @instrument("Tool._call", { attributes: { tool: "ReplaceInFileTool" } })
  async _call({
    fname,
    oldText,
    newText,
  }: z.infer<typeof schema>): Promise<string> {
    currentSpan().setAttributes({
      fname,
      oldText,
      newText,
    });

    try {
      const filePath = this.codeContext.resolveFile(fname);
      const fileContent = await readFileContent(filePath);

      const newContent = fileContent.replaceAll(oldText, newText);
      if (newContent !== fileContent) {
        await writeFileContent(filePath, newContent);

        await this.notifyFileModified(fname);
      }
      return "file successfully updated";
    } catch (error) {
      console.error(`Failed to update file: ${fname}`);
      console.error(error);
      return "failed to update file";
    }
  }
}