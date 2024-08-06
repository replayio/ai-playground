import { BaseAgent } from './base_agent';
import { BaseChatModel, BaseChatModelCallOptions } from '@langchain/core/language_models/chat_models';
import { BaseLanguageModel } from '@langchain/core/language_models/base';
import { getModelServiceCtor, ChatModelConstructor } from '../models/msn';
import { createReactAgent, AgentExecutor } from 'langchain/agents';
import { SystemMessage, HumanMessage, BaseMessage, AIMessage, AIMessageChunk, BaseMessageChunk, BaseMessageLike } from '@langchain/core/messages';
import { instrument } from '../instrumentation/instrument';
import { logger } from '../utils/logger';
import { Tool } from '@langchain/core/tools';
import { BaseMemory, BufferMemory } from 'langchain/memory';
import { ChatPromptTemplate, HumanMessagePromptTemplate, BasePromptTemplate } from '@langchain/core/prompts';
import { LLMResult, ChatResult, Generation, ChatGenerationChunk, ChatGeneration } from '@langchain/core/outputs';
import { RunnableConfig } from '@langchain/core/runnables';
import { CallbackManagerForLLMRun } from '@langchain/core/callbacks/manager';
import { BaseLanguageModelInput, BaseLanguageModelCallOptions } from '@langchain/core/language_models/base';

@instrument('Agent', [], { attributes: { tool: "Agent" } })
class Agent extends BaseAgent implements BaseChatModel<BaseLanguageModelCallOptions, BaseMessageChunk> {
  private model!: AgentExecutor;
  private tools: Tool[];
  private baseModel: BaseChatModel;
  private memory: BaseMemory;

  ParsedCallOptions!: BaseLanguageModelCallOptions;
  callKeys!: string[];
  lc_serializable = true;
  lc_kwargs: Record<string, unknown> = {};

  constructor(msnStr: string) {
    super();
    const ModelConstructor: ChatModelConstructor = getModelServiceCtor(msnStr);
    this.baseModel = ModelConstructor("default-model", null);
    this.memory = new BufferMemory();
    this.tools = [];
    this.ParsedCallOptions = this.baseModel.ParsedCallOptions;
    this.callKeys = this.baseModel.callKeys;
    const prompt = ChatPromptTemplate.fromMessages([
      new SystemMessage(this.getSystemPrompt()),
      HumanMessagePromptTemplate.fromTemplate("{input}"),
    ]);
    this.initializeAgent(this.baseModel, prompt);
  }

  private async initializeAgent(model: BaseChatModel, prompt: ChatPromptTemplate): Promise<void> {
    const agent = await createReactAgent({
      llm: model,
      tools: this.tools,
      prompt,
    });
    this.model = AgentExecutor.fromAgentAndTools({
      agent,
      tools: this.tools,
      memory: this.memory,
      returnIntermediateSteps: true,
    });
  }

  getSystemPrompt(): string {
    return "You are an AI assistant. Help the user with their tasks.";
  }

  preparePrompt(prompt: string): string {
    return `User request: ${prompt}\nPlease provide a helpful response.`;
  }

  @instrument('Agent.runPrompt', ['prompt'], { attributes: { tool: "Agent" } })
  async runPrompt(prompt: string): Promise<string> {
    console.log(`Running prompt: ${prompt}`);
    const preparedPrompt = this.preparePrompt(prompt);
    const modifiedFiles: Set<string> = new Set();

    try {
      const result = await this.model.invoke({ input: preparedPrompt });
      logger.debug(`Agent received result: ${JSON.stringify(result)}`);
      // Handle result here
      if (typeof result.output === 'string') {
        return result.output;
      } else {
        return JSON.stringify(result);
      }
    } catch (error) {
      console.error(`Error during prompt execution: ${error instanceof Error ? error.message : String(error)}`);
      throw error;
    }
  }

  @instrument('Agent.handleCompletion', ['hadAnyText', 'modifiedFiles'], { attributes: { tool: "Agent" } })
  public async handleCompletion(hadAnyText: boolean, modifiedFiles: Set<string>): Promise<void> {
    // Handle completion, show diffs, ask user to apply changes
    for (const file of modifiedFiles) {
      await this.handleModifiedFile(file);
    }
  }

  @instrument('Agent.handleModifiedFile', ['file'], { attributes: { tool: "Agent" } })
  private async handleModifiedFile(file: string): Promise<void> {
    // Handle modified file, show diff, ask user to apply changes
    console.log(`File modified: ${file}`);
    // Implement file modification handling logic here
    // This is a placeholder and should be replaced with actual implementation
  }

  // Implement BaseChatModel interface methods
  async generate(messages: BaseMessage[][], options?: BaseChatModelCallOptions): Promise<LLMResult> {
    return this.baseModel.generate(messages, options);
  }

  async generatePrompt(promptValues: BasePromptTemplate[], options?: BaseChatModelCallOptions): Promise<LLMResult> {
    return this.baseModel.generatePrompt(promptValues, options);
  }

  async call(messages: BaseMessage[], options?: BaseChatModelCallOptions): Promise<BaseMessage> {
    return this.baseModel.call(messages, options);
  }

  async predict(text: string, options?: BaseChatModelCallOptions): Promise<string> {
    return this.baseModel.predict(text, options);
  }

  async predictMessages(messages: BaseMessage[], options?: BaseChatModelCallOptions): Promise<BaseMessage> {
    return this.baseModel.predictMessages(messages, options);
  }

  async *_streamResponseChunks(
    messages: BaseMessage[],
    options: RunnableConfig,
    runManager?: CallbackManagerForLLMRun
  ): AsyncGenerator<ChatGenerationChunk, void, unknown> {
    try {
      for await (const chunk of this.baseModel._streamResponseChunks(messages, options, runManager)) {
        if (isChatGenerationChunk(chunk)) {
          yield chunk;
        } else if (isAIMessageChunk(chunk)) {
          const messageChunk = chunk as AIMessageChunk;
          const content = typeof messageChunk.content === 'string' ? messageChunk.content : JSON.stringify(messageChunk.content);
          yield new ChatGenerationChunk({
            text: content,
            message: messageChunk,
            generationInfo: {}
          });
        } else {
          console.warn('Unexpected chunk type:', chunk);
          yield new ChatGenerationChunk({
            text: '',
            message: new AIMessageChunk({ content: '' }),
            generationInfo: {}
          });
        }
      }
    } catch (error) {
      console.error('Error in _streamResponseChunks:', error);
      throw error;
    }
  }

  async _generateUncached(
    messages: BaseMessage[][],
    options: this['ParsedCallOptions'],
    runManager?: CallbackManagerForLLMRun
  ): Promise<LLMResult> {
    const result = await this.baseModel.generate(messages, options);
    return {
      generations: result.generations.map(gen => gen.map(g => ({
        text: g.text,
        message: g.message instanceof BaseMessage ? g.message : new AIMessage(g.text),
        generationInfo: g.generationInfo
      }))),
      llmOutput: result.llmOutput
    };
  }

  async _generateCached(
    messages: BaseMessage[][],
    options: this['ParsedCallOptions'],
    runManager?: CallbackManagerForLLMRun
  ): Promise<LLMResult> {
    const result = await this.baseModel.generate(messages, options);
    return {
      generations: result.generations.map(gen => gen.map(g => ({
        text: g.text,
        message: g.message || new AIMessage(g.text),
        generationInfo: g.generationInfo || {}
      }))),
      llmOutput: result.llmOutput
    };
  }

  async invoke(input: BaseLanguageModelInput, options?: RunnableConfig): Promise<BaseMessageChunk> {
    const result = await this.baseModel.invoke(input, options);
    return result as BaseMessageChunk;
  }
}

// Type guards
function isChatGenerationChunk(chunk: unknown): chunk is ChatGenerationChunk {
  return (
    typeof chunk === 'object' &&
    chunk !== null &&
    'text' in chunk &&
    'message' in chunk &&
    typeof (chunk as ChatGenerationChunk).text === 'string' &&
    typeof (chunk as ChatGenerationChunk).message === 'object'
  );
}

function isAIMessageChunk(chunk: unknown): chunk is AIMessageChunk {
  return (
    typeof chunk === 'object' &&
    chunk !== null &&
    'content' in chunk &&
    (typeof (chunk as AIMessageChunk).content === 'string' ||
      typeof (chunk as AIMessageChunk).content === 'object')
  );
}

export { Agent };
