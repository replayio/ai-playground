import { BaseAgent } from './base_agent';
import { BaseChatModel } from '@langchain/core/language_models/chat_models';
import { getModelServiceCtor, ChatModelConstructor } from '../models/msn';
import { createReactAgent } from '../utils/agent_utils';
import { AsyncSqliteSaver } from '../utils/sqlite_saver';
import { SystemMessage, HumanMessage, BaseMessage } from '@langchain/core/messages';
import { instrument } from '../instrumentation/instrument';
import { getArtifactsDir } from '../constants';
import { logger } from '../utils/logger';
import { Tool } from '@langchain/core/tools';

@instrument('Agent', [], { attributes: { tool: "Agent" } })
class Agent extends BaseAgent {
  model: BaseChatModel;
  private tools: Tool[];

  constructor(msnStr: string) {
    super();
    const ModelConstructor: ChatModelConstructor = getModelServiceCtor(msnStr);
    const model = ModelConstructor("default-model", null);
    const memory = new AsyncSqliteSaver();
    this.tools = []; // Initialize tools array
    this.model = createReactAgent(
      model,
      this.tools,
      memory
    );
  }

  getSystemPrompt(): string {
    // Implement the abstract method
    return "Default system prompt";
  }

  preparePrompt(prompt: string): string {
    // Implement the abstract method
    return `Prepared prompt: ${prompt}`;
  }

  @instrument('Agent.runPrompt', ['prompt'], { attributes: { tool: "Agent" } })
  async runPrompt(prompt: string): Promise<string> {
    console.log(`Running prompt: ${prompt}`);
    const system = new SystemMessage(this.getSystemPrompt());
    const msg = new HumanMessage(this.preparePrompt(prompt));
    const modifiedFiles: Set<string> = new Set();

    try {
      const events = await this.model.call([system, msg]);
      if (Array.isArray(events)) {
        for (const event of events) {
          if (typeof event === 'object' && event !== null && 'type' in event) {
            logger.debug(`Agent received event: ${event.type}`);
            // Handle events here
            // ...
          }
        }
      }
    } catch (error) {
      console.error(`Error during prompt execution: ${error instanceof Error ? error.message : String(error)}`);
      throw error;
    }

    await this.handleCompletion(true, modifiedFiles);
    return "Prompt execution completed";
  }

  @instrument('Agent.handleCompletion', ['hadAnyText', 'modifiedFiles'], { attributes: { tool: "Agent" } })
  public async handleCompletion(hadAnyText: boolean, modifiedFiles: Set<string>): Promise<void> {
    // Handle completion, show diffs, ask user to apply changes
    // Implement the completion logic here
    for (const file of modifiedFiles) {
      this.handleModifiedFile(file);
    }
  }

  @instrument('Agent.handleModifiedFile', ['file'], { attributes: { tool: "Agent" } })
  private handleModifiedFile(file: string): void {
    // Handle modified file, show diff, ask user to apply changes
    console.log(`File modified: ${file}`);
    // Implement file modification handling logic here
  }
}

export { Agent };
