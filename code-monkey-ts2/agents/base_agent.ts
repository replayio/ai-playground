import { StructuredTool } from "@langchain/core/tools";
import { CodeContext } from "../code_context";

export type PromptResult = string;

export abstract class BaseAgent {
  constructor(
    public name: string,
    public systemPrompt: string,
    public tools: StructuredTool[],
    protected _codeContext?: CodeContext
  ) {}

  get codeContext(): CodeContext | undefined {
    return this._codeContext;
  }

  useCodeContext(): CodeContext {
    if (!this._codeContext) {
      throw new Error(
        `[Agent ${this.name}] tried to access codeContext but has none.`
      );
    }
    return this._codeContext;
  }

  abstract runPrompt(prompt: string): Promise<PromptResult>;

  abstract preparePrompt(prompt: string): string;
}
