import { StructuredTool } from "@langchain/core/tools";
import { dispatchCustomEvent } from "@langchain/core/callbacks/dispatch";
import { CodeContext } from '../code_context';

export abstract class IOTool extends StructuredTool {
  protected codeContext: CodeContext;

  constructor(codeContext: CodeContext) {
    super();
    this.codeContext = codeContext;
  }

  async notifyFileModified(filePath: string): Promise<void> {
    await dispatchCustomEvent("file_modified", filePath);
  }
}
