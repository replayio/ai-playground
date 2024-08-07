import { ChatOpenAI } from "@langchain/openai";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { Tool } from "@langchain/core/tools";
import { AgentExecutor, createToolCallingAgent } from "langchain/agents";
import * as fs from 'fs';
import * as path from 'path';

import { askUser, showDiff } from '../tools/utils';
import { getRootDir, getArtifactsDir, getAgentMsn } from '../constants';
import { MSN } from '../models/msn';
import { BaseAgent } from './base_agent';
import { currentSpan, instrument } from '../instrumentation';
import { getLogger } from '../util/logs';

class Agent extends BaseAgent {
  private model: AgentExecutor;
  private config: { configurable: { thread_id: string } };

  constructor() {
    super();
    const msnStr = getAgentMsn();
    const msn = MSN.fromString(msnStr);

    const llm = msn.constructModel() as ChatOpenAI;
    const tools = this.tools as Tool[];
    
    const prompt = ChatPromptTemplate.fromMessages([
      ["system", this.getSystemPrompt()],
      ["human", "{input}"],
      ["placeholder", "{agent_scratchpad}"],
    ]);
    
    const agent = createToolCallingAgent({
      llm,
      tools,
      prompt,
    });

    this.model = new AgentExecutor({
      agent,
      tools,
    });

    this.config = {
      configurable: { thread_id: "abc123" },
    };

    this.initialize();
  }

  // Custom Agent initialization goes here, when necessary.
  @instrument("Agent.initialize", ["msn_str"])
  initialize(): void {}

  preparePrompt(prompt: string): string {
    return prompt;
  }

  @instrument("Agent.runPrompt", ["prompt"])
  async runPrompt(prompt: string): Promise<string> {
    const logger = getLogger();
    logger.info(`Running prompt: ${prompt}`);

    const input = this.preparePrompt(prompt);

    const modifiedFiles: Set<string> = new Set();
    let result: string | null = null;

    const response = await this.model.invoke({ input });

    result = response.output;

    // Assuming the agent might modify files during execution
    // You may need to adjust this part based on how your agent actually modifies files
    if ('intermediateSteps' in response) {
      for (const step of response.intermediateSteps) {
        if (step.action.tool === 'file_modified') {
          modifiedFiles.add(step.action.toolInput as string);
        }
      }
    }

    this.handleCompletion(modifiedFiles);

    logger.debug(`[AGENT ${this.name}] run_prompt result: "${result || ""}"`);
    return result || "";
  }

  @instrument("Agent.handleCompletion")
  handleCompletion(modifiedFiles: Set<string>): void {
    const span = currentSpan();
    span.setAttributes({
      "num_modified_files": modifiedFiles.size,
      "modified_files": Array.from(modifiedFiles).join(", "),
    });

    if (modifiedFiles.size > 0) {
      for (const file of modifiedFiles) {
        this.handleModifiedFile(file);
      }
    }
  }

  @instrument("Agent.handleModifiedFile", ["file"])
  handleModifiedFile(file: string): void {
    const originalFile = path.join(getRootDir(), file);
    const modifiedFile = path.join(getArtifactsDir(), file);
    showDiff(originalFile, modifiedFile);
    const response = askUser(
      `Do you want to apply the changes to ${file} (diff shown in VSCode)? (Y/n): `
    ).toLowerCase();

    const applyChanges = response === "y" || response === "";

    currentSpan().setAttribute("apply_changes", applyChanges);

    if (applyChanges) {
      this.applyChanges(originalFile, modifiedFile);
      console.log(`✅ Changes applied to ${file}`);
    } else {
      console.log(`❌ Changes not applied to ${file}`);
    }
  }

  @instrument("Agent.applyChanges", ["originalFile", "modifiedFile"])
  applyChanges(originalFile: string, modifiedFile: string): void {
    const modifiedContent = fs.readFileSync(modifiedFile, 'utf8');
    fs.writeFileSync(originalFile, modifiedContent);
  }
}

export default Agent;