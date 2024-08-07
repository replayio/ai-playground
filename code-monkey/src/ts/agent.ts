import { promises as fs } from 'fs';
import * as path from 'path';
import { ChatOpenAI } from '@langchain/openai';
import { getRootDir, getArtifactsDir, getAgentMsn } from './constants';
import { askUser, showDiff } from './utils';
import { Tool, DynamicTool } from '@langchain/core/tools';
import { AgentExecutor, initializeAgentExecutorWithOptions } from 'langchain/agents';
import { BufferMemory } from 'langchain/memory';
import { AsyncSqliteSaver } from './async_sqlite_saver';

// Temporarily remove the @instrument decorator
class Agent {
    private model: ChatOpenAI;
    protected tools: Tool[];
    private memory: BufferMemory;
    private executor: AgentExecutor | null;
    private saver: AsyncSqliteSaver;

    private config = {
        configurable: { thread_id: 'abc123' },
    };

    constructor() {
        const msnStr = getAgentMsn();
        this.model = new ChatOpenAI({ modelName: msnStr });

        this.tools = this.initializeTools();
        this.memory = this.createMemory();
        this.saver = new AsyncSqliteSaver();
        this.executor = null;
    }

    async initialize(): Promise<void> {
        this.executor = await this.createReactAgent(this.model);
    }

    private initializeTools(): Tool[] {
        return [
            new DynamicTool({
                name: "ask_user",
                description: "Ask the user a question and get their response",
                func: async (question: string) => {
                    return await askUser(question);
                },
            }),
            new DynamicTool({
                name: "show_diff",
                description: "Show the diff between two files",
                func: async (input: string) => {
                    const [originalFile, modifiedFile] = input.split(',');
                    await showDiff(originalFile.trim(), modifiedFile.trim());
                    return "Diff shown successfully";
                },
            }),
            // Add more tools as needed, following the langchain.js v0.2 guidelines
        ];
    }

    private createMemory(): BufferMemory {
        return new BufferMemory({
            returnMessages: true,
            memoryKey: "chat_history",
            inputKey: "input",
        });
    }

    preparePrompt(prompt: string): string {
        return prompt;
    }

    // Temporarily remove the @instrument decorator
    async runPrompt(prompt: string): Promise<string> {
        if (!this.executor) {
            throw new Error("Agent not initialized. Call initialize() before running prompts.");
        }

        console.log(`Running prompt: ${prompt}`);

        const modifiedFiles: Set<string> = new Set();

        const result = await this.executor.call({ input: this.preparePrompt(prompt) });

        await this.handleCompletion(modifiedFiles);

        // Save the result using AsyncSqliteSaver
        try {
            await this.saver.save(
                this.config.configurable.thread_id,
                result.output
            );
        } catch (error) {
            console.error('Error saving result:', error);
            // Optionally, you can choose to throw the error or handle it differently
        }

        return result.output;
    }

    // Temporarily remove the @instrument decorator
    private async handleCompletion(modifiedFiles: Set<string>): Promise<void> {
        if (modifiedFiles.size > 0) {
            for (const file of modifiedFiles) {
                await this.handleModifiedFile(file);
            }
        }
    }

    // Temporarily remove the @instrument decorator
    private async handleModifiedFile(file: string): Promise<void> {
        const originalFile = path.join(getRootDir(), file);
        const modifiedFile = path.join(getArtifactsDir(), file);
        await showDiff(originalFile, modifiedFile);
        const response = await askUser(
            `Do you want to apply the changes to ${file} (diff shown in VSCode)? (Y/n): `
        );

        const applyChanges = response.toLowerCase() === 'y' || response === '';

        if (applyChanges) {
            await this.applyChanges(originalFile, modifiedFile);
            console.log(`✅ Changes applied to ${file}`);
        } else {
            console.log(`❌ Changes not applied to ${file}`);
        }
    }

    // Temporarily remove the @instrument decorator
    private async applyChanges(originalFile: string, modifiedFile: string): Promise<void> {
        const modifiedContent = await fs.readFile(modifiedFile, 'utf8');
        await fs.writeFile(originalFile, modifiedContent);
    }

    private async createReactAgent(model: ChatOpenAI): Promise<AgentExecutor> {
        return await initializeAgentExecutorWithOptions(
            this.tools,
            model,
            {
                agentType: "structured-chat-zero-shot-react-description",
                verbose: true,
                memory: this.memory,
                returnIntermediateSteps: true
            }
        );
    }

    protected getSystemPrompt(): string {
        return `You are an AI assistant designed to help with various tasks. Your goal is to understand and respond to user queries effectively.

Instructions:
1. Analyze the user's request carefully.
2. Use the available tools when necessary to gather information or perform actions.
3. Provide clear and concise responses.
4. If you're unsure about something, ask for clarification.
5. Always prioritize the user's safety and adhere to ethical guidelines.

Let's work together to solve problems and answer questions!`;
    }
}

export { Agent };
