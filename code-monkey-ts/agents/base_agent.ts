import { Tool } from '@langchain/core/tools';

abstract class BaseAgent {
    tools: Tool[] | null = null;
    SYSTEM_PROMPT = "You don't know what to do. Tell the user that they can't use you and must use an agent with a proper SYSTEM_PROMPT instead.";

    get name() {
        return this.constructor.name;
    }

    abstract runPrompt(prompt: string): Promise<string>;

    getSystemPrompt(): string {
        return this.SYSTEM_PROMPT;
    }

    abstract preparePrompt(prompt: string): string;

    abstract handleCompletion(modifiedFiles: Set<string>): void;
}

export { BaseAgent };
