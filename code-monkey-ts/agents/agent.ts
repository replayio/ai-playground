import fs from "fs";
import path from "path";
import { randomUUID } from "crypto";

import { createReactAgent } from "@langchain/langgraph/prebuilt";
import { MemorySaver } from "@langchain/langgraph";
import { HumanMessage, SystemMessage } from "@langchain/core/messages";
import { StructuredTool } from "@langchain/core/tools";
import { Attributes } from "@opentelemetry/api";

import { instrument, currentSpan, withKVBaggage } from "../instrumentation";
import { getAgentConfig } from "../config";
import { MSN } from "../models";
import { showDiff, askUser } from "../tools/utils";

import { BaseAgent, PromptResult } from "./base_agent";
import { CodeContext } from "../code_context";

function debugLog(...args: any[]): void {
  console.debug(...args);
}

type TokenUsage = {
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
};

export abstract class Agent extends BaseAgent {
  msn: MSN;
  model: ReturnType<typeof createReactAgent>;

  config = {
    configurable: { thread_id: randomUUID() },
  };

  // TODO(class decorator here) @instrument("Agent.__init__", ["msn_str"])
  constructor(
    systemPrompt: string,
    tools: StructuredTool[],
    codeContext?: CodeContext
  ) {
    super(systemPrompt, tools, codeContext);

    const name = this.constructor.name;
    const { msn: msnStr } = getAgentConfig(name);
    this.msn = MSN.from_string(msnStr);

    // a checkpointer + the thread_id below gives the model a way to save its
    // state so we don't have to accumulate the messages ourselves.
    const checkpointer = new MemorySaver();
    this.model = createReactAgent({
      llm: this.msn.constructModel(),
      tools: this.tools,
      checkpointSaver: checkpointer,
    });
  }

  /**
   * The `initialize` method cannot be overwritten.
   * If needed, override `handleInitialize` instead.
   */
  public readonly initialize = async (): Promise<void> => {
    await this.codeContext?.indexFiles();
    await this.handleInitialize();
  };

  protected async handleInitialize(): Promise<void> {}

  getKVBaggageAttributes(): Attributes {
    return {
      agent: this.name,
      "msn.service": this.msn.chatModelService,
      "msn.model_name": this.msn.modelName,
      "msn.flags": JSON.stringify(this.msn.flags),
    };
  }

  preparePrompt(prompt: string): string {
    // TODO: known_files cost several hundred tokens for a small project.
    if (this._codeContext) {
      return `
These are all files: \`[${this._codeContext.knownFiles}]\`.
${prompt.trim()}
    `.trim();
    }
    return prompt.trim();
  }

  async runPrompt(prompt: string): Promise<PromptResult> {
    return withKVBaggage(
      this.getKVBaggageAttributes(),
      async (): Promise<string> => {
        return await this._runPrompt(prompt);
      },
    );
  }

  @instrument("Agent.runPrompt")
  private async _runPrompt(prompt: string): Promise<PromptResult> {
    currentSpan().setAttributes({
      prompt,
    });

    // TODO
    // logger = get_logger(__name__)
    // logger.info(`Running prompt: {prompt}`);

    console.log(
      // `[AGENT ${this.name}] Running prompt: ${JSON.stringify(prompt)}`
      `[AGENT ${this.name}] Running prompt: ${prompt}`
    );
    const system = new SystemMessage({
      content: this.systemPrompt,
    });
    const msg = new HumanMessage({
      content: this.preparePrompt(prompt),
    });

    const modified_files: Set<string> = new Set();
    let result: string | null = null;

    const tokenUsage: TokenUsage = {
      input_tokens: 0,
      output_tokens: 0,
      total_tokens: 0,
    };

    for await (const event of this.model.streamEvents(
      {
        messages: [system, msg],
      },
      {
        configurable: this.config.configurable,
        version: "v2",
      }
    )) {
      if (event.data?.output?.usage_metadata) {
        const { input_tokens, output_tokens, total_tokens } =
          event.data.output.usage_metadata;
        tokenUsage.input_tokens += input_tokens;
        tokenUsage.output_tokens += output_tokens;
        tokenUsage.total_tokens += total_tokens;
      }

      const kind = event.event;
      if (
        kind != "on_chat_model_stream" &&
        kind != "on_chain_end" &&
        kind != "on_chain_stream" &&
        kind != "on_chain_start"
      ) {
        debugLog(
          `[AGENT ${this.name}] received event: ${kind}`
          // `[AGENT ${this.name}] received event: ${JSON.stringify(event, null, 2)}`,
        );
      }

      if (kind == "on_chat_model_start") {
        // for msg in event.data.input["messages"][0]:
        //     print("----")
        //     print(msg.content)
        continue;
      }

      if (kind == "on_chat_model_stream") {
        // NB(toshok) we can stream text as it comes in by doing it here,
        // but I'm doing the entire thing in one go in the
        // on_chat_model_end event just below.
        continue;
      }

      if (kind == "on_tool_start") {
        // TODO
        const tool_name = event.name;
        const tool_input = event.data.input;
        debugLog(
          `[AGENT ${
            this.name
          }] ${kind} - name=${tool_name}, input=${JSON.stringify(tool_input)}`
        );
        continue;
      }

      if (kind == "on_tool_end") {
        const tool_name = event.name;
        const tool_output = event.data.output.content.slice(0, 20);
        debugLog(
          `[AGENT ${
            this.name
          }] ${kind} - name=${tool_name}, output=${JSON.stringify(tool_output)}`
        );
        continue;
      }

      if (kind == "on_chat_model_end") {
        const { content } = event.data.output;
        // anthropic seems give us content as a list?
        result = Array.isArray(content) ? content[0]["text"] : content;
        console.log(`[AGENT ${this.name}] RESULT: ${result}`);
        continue;
      }

      if (kind == "on_custom_event") {
        // TODO(toshok) a better dispatch mechanism would be nice, but
        // there's only one event type currently
        if (event.name === "file_modified") {
          modified_files.add(event.data as string);
        } else {
          debugLog(
            `[AGENT ${this.name}] Unknown prompt event: '${event["name"]}'`
          );
        }
        continue;
      }
    }

    if (tokenUsage.total_tokens > 0) {
      currentSpan().setAttributes(tokenUsage);
    }

    await this.handleCompletion(modified_files);

    result = result?.trim() || "";
    debugLog(`[AGENT ${this.name}] runPrompt END: "${result}"`);
    return result;
  }

  @instrument("Agent.handleCompletion")
  private async handleCompletion(modified_files: Set<string>): Promise<void> {
    currentSpan().setAttributes({
      num_modified_files: modified_files.size,
      modified_files: Array.from(modified_files).join(", "),
    });

    for (const file of Array.from(modified_files)) {
      if (this.useCodeContext().artifactsDir) {
        await this.handleModifiedFile(file);
      } else {
        console.log(`✅ Changed file "${file}"`);
      }
    }
  }

  @instrument("Agent.handle_modified_file")
  private async handleModifiedFile(file: string): Promise<void> {
    currentSpan().setAttributes({
      file,
    });
    const original_file = path.join(this.useCodeContext().originalDir, file);
    const modified_file = path.join(this.useCodeContext().artifactsDir!, file);
    showDiff(original_file, modified_file);
    const response = (
      await askUser(
        `Do you want to apply the changes to ${file} (diff shown in VSCode)? (Y/n): `
      )
    ).toLowerCase();

    const apply_changes = response == "y" || response == "";

    // TODO
    // current_span().set_attribute("apply_changes", apply_changes)

    if (apply_changes) {
      this.applyChanges(original_file, modified_file);
      console.log(`✅ Changes applied to ${file}`);
    } else {
      console.log(`❌ Changes not applied to ${file}`);
    }
  }

  @instrument("Agent.applyChanges")
  private applyChanges(original_file: string, modified_file: string): void {
    currentSpan().setAttributes({
      original_file,
      modified_file,
    });

    // TODO(toshok) we probably want the before/after size?  or something about size of the diff
    const modified_content = fs.readFileSync(modified_file, "utf8");
    fs.writeFileSync(original_file, modified_content);
  }
}

export type AgentConstructor = new (codeContext: CodeContext) => Agent;
