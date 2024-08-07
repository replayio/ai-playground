import { AIMessage, BaseMessage, HumanMessage, SystemMessage } from "@langchain/core/messages";
import { Tool } from "@langchain/core/tools";
import { ChatAnthropic } from "@langchain/anthropic";
import { StateGraph, StateGraphArgs } from "@langchain/langgraph";
import { MemorySaver } from "@langchain/langgraph";
import { ToolNode, createReactAgent } from "@langchain/langgraph/prebuilt";
import { PromptTemplate } from "@langchain/core/prompts";
import fs from 'fs';
import path from 'path';
import { getRootDir, getArtifactsDir, getAgentMsn } from '../constants';
import { MSN } from '../models/msn';
import { askUser, showDiff } from '../tools/utils';
import { instrument, currentSpan } from '../instrumentation';
import Logger from '../logger';

interface AgentState {
  messages: BaseMessage[];
}

export class Agent {
  private model: ChatAnthropic;
  private workflow: any; // The compiled StateGraph
  private checkpointer: MemorySaver;
  private executor: AgentExecutor;
  static tools: BaseTool[];
  static SYSTEM_PROMPT: string;

  @instrument('Agent.__init__', ['msn_str'])
  constructor() {
    const msnStr = getAgentMsn();
    const msn = MSN.fromString(msnStr);

    this.model = new ChatAnthropic({
      modelName: msn.modelName,
      temperature: 0,
    });

    this.initialize();
  }

  async initialize(): Promise<void> {
    const toolNode = new ToolNode<AgentState>(tools);

    this.model = this.model.bind({ tools });

    // Create ReAct agent
    const prompt = await pull<PromptTemplate>("hwchase17/react");
    const agent = await createReactAgent({
      llm: this.model,
      tools: (this.constructor as typeof Agent).tools,
      prompt,
    });

    this.executor = new AgentExecutor({
      agent,
      tools,
    });

    const graphState: StateGraphArgs<AgentState>["channels"] = {
      messages: {
        reducer: (x: BaseMessage[], y: BaseMessage[]) => x.concat(y),
      },
    };

    const workflow = new StateGraph<AgentState>({ channels: graphState })
      .addNode("agent", this.callAgent.bind(this))
      .addNode("tools", toolNode)
      .addEdge("__start__", "agent")
      .addConditionalEdges("agent", this.shouldContinue)
      .addEdge("tools", "agent");

    this.checkpointer = new MemorySaver();
    this.workflow = workflow.compile({ checkpointer: this.checkpointer });
  }

  getTools(): Tool[] {
    return [
      new Tool({
        name: "file_modified",
        description: "Notifies when a file has been modified.",
        func: async ({ file }: { file: string }) => {
          // Implement file modification logic
          return `File ${file} has been modified.`;
        },
      }),
    ];
  }

  async callAgent(state: AgentState) {
    const messages = state.messages;
    const result = await this.executor.invoke({ input: messages[messages.length - 1].content, chat_history: messages });
    return { messages: [...messages, new AIMessage(result.output)] };
  }

  shouldContinue(state: AgentState) {
    const messages = state.messages;
    const lastMessage = messages[messages.length - 1] as AIMessage;

    if (lastMessage.additional_kwargs?.tool_calls?.length) {
      return "tools";
    }
    return "__end__";
  }

  @instrument('Agent.runPrompt', ['prompt'])
  async runPrompt(prompt: string): Promise<string> {
    const logger = Logger.getLogger(__filename);
    logger.info(`Running prompt: ${prompt}`);

    const systemMessage = new SystemMessage(this.getSystemPrompt());
    const humanMessage = new HumanMessage(this.preparePrompt(prompt));

    const finalState = await this.workflow.invoke(
      { messages: [systemMessage, humanMessage] },
      { configurable: { thread_id: "agent_thread" } }
    );

    const result = finalState.messages[finalState.messages.length - 1].content;
    console.log(result);

    await this.handleCompletion(this.getModifiedFiles(finalState));

    return result;
  }

  getModifiedFiles(finalState: AgentState): Set<string> {
    const modifiedFiles = new Set<string>();
    for (const message of finalState.messages) {
      if ('additional_kwargs' in message && message.additional_kwargs.tool_calls) {
        for (const toolCall of message.additional_kwargs.tool_calls) {
          if (toolCall.function.name === 'file_modified') {
            const args = JSON.parse(toolCall.function.arguments);
            modifiedFiles.add(args.file);
          }
        }
      }
    }
    return modifiedFiles;
  }

  @instrument('Agent.handleCompletion')
  private async handleCompletion(modifiedFiles: Set<string>): Promise<void> {
    const span = currentSpan();
    span.setAttributes({
      num_modified_files: modifiedFiles.size,
      modified_files: Array.from(modifiedFiles).join(', '),
    });

    for (const file of modifiedFiles) {
      await this.handleModifiedFile(file);
    }
  }

  @instrument('Agent.handleModifiedFile', ['file'])
  private async handleModifiedFile(file: string): Promise<void> {
    const originalFile = path.join(getRootDir(), file);
    const modifiedFile = path.join(getArtifactsDir(), file);
    
    showDiff(originalFile, modifiedFile);
    const response = await askUser(`Do you want to apply the changes to ${file} (diff shown in VSCode)? (Y/n): `);

    const applyChanges = response.toLowerCase() === 'y' || response === '';

    currentSpan().setAttribute('apply_changes', applyChanges);

    if (applyChanges) {
      await this.applyChanges(originalFile, modifiedFile);
      console.log(`✅ Changes applied to ${file}`);
    } else {
      console.log(`❌ Changes not applied to ${file}`);
    }
  }

  @instrument('Agent.applyChanges', ['originalFile', 'modifiedFile'])
  private async applyChanges(originalFile: string, modifiedFile: string): Promise<void> {
    const modifiedContent = await fs.promises.readFile(modifiedFile, 'utf-8');
    await fs.promises.writeFile(originalFile, modifiedContent);
  }

  preparePrompt(prompt: string): string {
    return prompt;
  }

  getSystemPrompt(): string {
    // Implement your system prompt logic here
    return "You are a helpful AI assistant.";
  }
}