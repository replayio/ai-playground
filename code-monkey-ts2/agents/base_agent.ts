import { z } from "zod";
import { StructuredTool } from "@langchain/core/tools";


export abstract class BaseAgent {
    constructor(
        public name: string,
        public systemPrompt: string,
        public tools: StructuredTool[],
    ) {}

    abstract runPrompt(prompt: string): Promise<string>;

    abstract preparePrompt(prompt: string): string;

    abstract handleCompletion(modified_files: Set<string>): void;
};
