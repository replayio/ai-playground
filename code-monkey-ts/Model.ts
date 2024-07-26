import { BaseAgent } from './agents/BaseAgent';

export enum ModelName {
    Noop = "noop",
    OpenAI = "openai",
    Anthropic = "anthropic"
}

export abstract class Model {
    name: ModelName;
    agent: BaseAgent;

    constructor() {}

    abstract runPrompt(prompt: string): Promise<string>;
}
