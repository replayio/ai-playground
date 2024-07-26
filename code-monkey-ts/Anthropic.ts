import { BaseAgent } from './agents/BaseAgent';
import { Model, ModelName } from './Model';
import { Anthropic, Message, MessageParam } from '@anthropic-ai/sdk';
import { TokenStats } from './TokenStats';
import { getToolSpecs, handleToolCall } from './tools/tools';
import { parseMsn } from './msn';

const DEFAULT_MSN = "anthropic/claude-3-5-sonnet-20240620/anthropic-beta=max-tokens-3-5-sonnet-2024-07-15";
const MAX_TOKENS = 8192;

enum EnvVars {
    API_KEY = "ANTHROPIC_API_KEY",
    MAX_TOKENS = "MAX_TOKENS"
}

function getMaxTokens(): number {
    return parseInt(process.env[EnvVars.MAX_TOKENS] || "1000");
}

export class AnthropicModel extends Model {
    name = ModelName.Anthropic;
    private client: Anthropic;
    private selectedModel: string;
    private extraHeaders: Record<string, string>;
    private tokenStats: TokenStats;

    constructor(agent: BaseAgent, msn?: string) {
        super();
        const apiKey = process.env[EnvVars.API_KEY];
        if (!apiKey) {
            throw new Error(`API Key was not defined. Make sure ${EnvVars.API_KEY} is in your .env.secret file`);
        }

        this.agent = agent;

        if (!msn) {
            msn = DEFAULT_MSN;
        }
        const [_, model, extraFlags] = parseMsn(msn);
        console.log(`AnthropicModel: model=${model}, extra_flags=${extraFlags}`);
        this.client = new Anthropic({ apiKey });
        this.selectedModel = model;
        this.extraHeaders = extraFlags;
        this.tokenStats = new TokenStats();
    }

    async runPrompt(prompt: string): Promise<string> {
        prompt = this.agent.preparePrompt(prompt);
        const modifiedFiles = new Set<string>();
        let hadAnyText = false;
        let assistantMessages: any[] = [];
        let userMessages: MessageParam[] = [{ role: "user", content: prompt }];
        let messages: MessageParam[] = userMessages;
        let finalMessageContent = "";

        try {
            while (true) {
                const response = await this._getClaudeResponse(messages);
                this.tokenStats.update(
                    response.usage.inputTokens,
                    response.usage.outputTokens,
                    response.content
                );
                assistantMessages = [];
                userMessages = [];

                this.tokenStats.printStats();

                const result = this._processResponse(
                    response,
                    modifiedFiles,
                    hadAnyText,
                    assistantMessages,
                    userMessages
                );
                hadAnyText = result.hadAnyText;
                finalMessageContent = result.finalMessageContent;

                if (userMessages.length === 0) {
                    if (this._handleCompletion(hadAnyText, modifiedFiles)) {
                        break;
                    }
                }

                messages = [
                    ...messages,
                    { role: "assistant", content: assistantMessages },
                    { role: "user", content: userMessages },
                ];
            }
        } finally {
            this.tokenStats.printStats();
        }

        return finalMessageContent;
    }

    private async _getClaudeResponse(messages: MessageParam[]): Promise<Message> {
        this.tokenStats.checkRateLimit();
        try {
            const response = await this.client.messages.create({
                temperature: 0,
                system: this.agent.getSystemPrompt(),
                model: this.selectedModel,
                max_tokens: getMaxTokens(),
                messages: messages,
                tools: getToolSpecs(this.agent.getTools()),
                extra_headers: this.extraHeaders,
            });
            return response;
        } catch (err) {
            console.error("##########################################################");
            console.error("PROMPT ERROR with the following messages:");
            console.error(JSON.stringify(messages, null, 2));
            console.error("##########################################################");
            throw err;
        }
    }

    private _processResponse(
        response: Message,
        modifiedFiles: Set<string>,
        hadAnyText: boolean,
        assistantMessages: any[],
        userMessages: any[]
    ): { hadAnyText: boolean; finalMessageContent: string } {
        let finalMessageContent = "";
        for (const responseMessage of response.content) {
            assistantMessages.push(responseMessage);

            if (responseMessage.type === "tool_use") {
                const toolResult = this._handleToolUse(responseMessage, modifiedFiles);
                userMessages.push(toolResult);
            } else if (responseMessage.type === "text") {
                hadAnyText = true;
                finalMessageContent = responseMessage.text;
                console.log(`A: ${finalMessageContent}`);
            } else if (responseMessage.type === "error") {
                hadAnyText = true;
                finalMessageContent = responseMessage.text;
                console.error(`ERROR: ${finalMessageContent}`);
                return { hadAnyText, finalMessageContent };
            } else if (responseMessage.type === "final") {
                hadAnyText = true;
                finalMessageContent = JSON.stringify(responseMessage);
                console.log(`DONE: ${finalMessageContent}`);
                return { hadAnyText, finalMessageContent };
            } else {
                throw new Error(`Unhandled message type: ${responseMessage.type} - ${JSON.stringify(responseMessage)}`);
            }
        }

        return { hadAnyText, finalMessageContent };
    }

    private _handleToolUse(responseMessage: any, modifiedFiles: Set<string>): any {
        const toolName: string = responseMessage.name;
        const tool = this.agent.getTool(toolName);
        if (!tool) {
            throw new Error(`Unknown tool: ${toolName}`);
        }

        return handleToolCall(
            responseMessage.id,
            responseMessage.input,
            modifiedFiles,
            tool
        );
    }

    private _handleCompletion(hadAnyText: boolean, modifiedFiles: Set<string>): boolean {
        return this.agent.handleCompletion(hadAnyText, modifiedFiles);
    }
}

// Note: You'll need to implement a registerModelService function in TypeScript
// registerModelService(ModelName.Anthropic, AnthropicModel);