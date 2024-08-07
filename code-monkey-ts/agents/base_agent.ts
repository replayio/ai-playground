import { Tool } from '@langchain/core/tools';

abstract class BaseAgent {
    static tools: Tool[] | null = null;
    static SYSTEM_PROMPT = "You don't know what to do. Tell the user that they can't use you and must use an agent with a proper SYSTEM_PROMPT instead.";

    abstract runPrompt(prompt: string): Promise<string>;

    getSystemPrompt(): string {
        return BaseAgent.SYSTEM_PROMPT;
    }

    abstract preparePrompt(prompt: string): string;

    abstract handleCompletion(hadAnyText: boolean, modifiedFiles: Set<string>): void;
}

export { BaseAgent };
