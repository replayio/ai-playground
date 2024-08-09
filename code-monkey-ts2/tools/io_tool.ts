import { StructuredTool } from "@langchain/core/tools";
import { dispatchCustomEvent } from "@langchain/core/callbacks/dispatch";

export abstract class IOTool extends StructuredTool {
  async notifyFileModified(filePath: string): Promise<void> {
    await dispatchCustomEvent("file_modified", filePath);
  }
}
