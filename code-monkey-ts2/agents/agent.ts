import fs from "fs";
import path from "path";
import { randomUUID } from "crypto";

import { createReactAgent } from "@langchain/langgraph/prebuilt";
import { MemorySaver } from "@langchain/langgraph";
import { HumanMessage, SystemMessage } from "@langchain/core/messages";
import { StructuredTool } from "@langchain/core/tools";

import { instrument, currentSpan } from "../instrumentation";
import { getAgentConfig } from "../config";
import { getRootDir, getArtifactsDir } from "../constants";
import { MSN } from "../models";
import { showDiff, askUser } from "../tools/utils";

import { BaseAgent } from "./base_agent";

function debugLog(...args: any[]) {
  console.debug(...args);
}

export abstract class Agent extends BaseAgent {
  model: ReturnType<typeof createReactAgent>;

  config = {
    configurable: { thread_id: randomUUID() },
  };

  // TODO(class decorator here) @instrument("Agent.__init__", ["msn_str"])
  constructor(name: string, systemPrompt: string, tools: StructuredTool[]) {
    super(name, systemPrompt, tools);

    console.log(`Agent ${name} constructor`);
    const { msn: msn_str } = getAgentConfig(name);
    const msn = MSN.from_string(msn_str);

    // a checkpointer + the thread_id below gives the model a way to save its
    // state so we don't have to accumulate the messages ourselves.
    const checkpointer = new MemorySaver();
    this.model = createReactAgent({
      llm: msn.constructModel(),
      tools: this.tools,
      checkpointSaver: checkpointer,
    });
  }

  async initialize(): Promise<void> {}

  preparePrompt(prompt: string): string {
    return prompt;
  }

  @instrument("Agent.runPrompt")
  async runPrompt(prompt: string): Promise<string> {
    currentSpan().setAttributes({
      agent: this.name,
      prompt,
    });
    // TODO
    // logger = get_logger(__name__)
    // logger.info(`Running prompt: {prompt}`);

    console.log(`[AGENT ${this.name}] Running prompt: ${prompt}`);
    const system = new SystemMessage({
      content: this.systemPrompt,
    });
    const msg = new HumanMessage({
      content: this.preparePrompt(prompt),
    });

    const modified_files: Set<string> = new Set();
    let result: string | null = null;

    for await (const event of this.model.streamEvents(
      {
        messages: [system, msg],
      },
      {
        configurable: this.config.configurable,
        version: "v2",
      },
    )) {
      const kind = event.event;

      if (
        kind != "on_chat_model_stream" &&
        kind != "on_chain_end" &&
        kind != "on_chain_stream" &&
        kind != "on_chain_start"
      ) {
        debugLog(
          `[AGENT ${this.name}] received event: ${JSON.stringify(event, null, 2)}`,
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
          `[AGENT ${this.name}] ${kind} - name=${tool_name}, input=${JSON.stringify(tool_input)}`,
        );
        continue;
      }

      if (kind == "on_tool_end") {
        const tool_name = event.name;
        const tool_output = event.data.output.content.slice(0, 20);
        debugLog(
          `[AGENT ${this.name}] ${kind} - name=${tool_name}, output=${JSON.stringify(tool_output)}`,
        );
        continue;
      }

      if (kind == "on_chat_model_end") {
        if (Array.isArray(event.data.output["content"])) {
          // anthropic seems give us content as a list?
          result = event.data.output["content"][0]["text"];
        } else {
          result = event.data.output.content;
        }
        debugLog(`[AGENT ${this.name}] RESULT: ${result}`);
        // TODO(toshok) still need to compute tokens
        continue;
      }

      if (kind == "on_custom_event") {
        // TODO(toshok) a better dispatch mechanism would be nice, but
        // there's only one event type currently
        if (event.name === "file_modified") {
          modified_files.add(event.data as string);
        } else {
          debugLog(
            `[AGENT ${this.name}] Unknown prompt event: '${event["name"]}'`,
          );
        }
        continue;
      }
    }

    await this.handleCompletion(modified_files);

    debugLog(`[AGENT ${this.name}] runPrompt result: "${result || ""}"`);
    return result || "";
  }

  @instrument("Agent.handleCompletion")
  async handleCompletion(modified_files: Set<string>): Promise<void> {
    currentSpan().setAttributes({
      agent: this.name,
      num_modified_files: modified_files.size,
      modified_files: Array.from(modified_files).join(", "),
    });

    for (const file of Array.from(modified_files)) {
      await this.handleModifiedFile(file);
    }
  }

  @instrument("Agent.handle_modified_file")
  async handleModifiedFile(file: string): Promise<void> {
    currentSpan().setAttributes({
      agent: this.name,
      file,
    });
    const original_file = path.join(getRootDir(), file);
    const modified_file = path.join(getArtifactsDir(), file);
    showDiff(original_file, modified_file);
    const response = (
      await askUser(
        `Do you want to apply the changes to ${file} (diff shown in VSCode)? (Y/n): `,
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
  applyChanges(original_file: string, modified_file: string): void {
    currentSpan().setAttributes({
      agent: this.name,
      original_file,
      modified_file,
    });

    // TODO(toshok) we probably want the before/after size?  or something about size of the diff
    const modified_content = fs.readFileSync(modified_file, "utf8");
    fs.writeFileSync(original_file, modified_content);
  }
}
