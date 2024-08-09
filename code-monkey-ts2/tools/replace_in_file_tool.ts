import { z } from "zod";
import { makeFilePath, readFileContent, writeFileContent } from "./utils";
import { instrument, currentSpan } from "../instrumentation";
import { IOTool } from "./io_tool";

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

  @instrument("Tool._call", { tool: "ReplaceInFileTool" })
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
      const filePath = makeFilePath(fname);
      const fileContent = (await readFileContent(filePath)).toString();

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
