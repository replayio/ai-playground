import fs from "fs";
import path from "path";
import { randomUUID } from "crypto";

import { createReactAgent } from "@langchain/langgraph/prebuilt";
import { MemorySaver } from "@langchain/langgraph";
import { HumanMessage, SystemMessage } from "@langchain/core/messages";
import { StructuredTool } from "@langchain/core/tools";

// TODO import { instrument } from "../instrumentation";
import { getRootDir, getArtifactsDir, getAgentMSN } from "../constants";
import { MSN } from "../models";
import { showDiff, askUser } from "../tools/utils";

import { BaseAgent } from "./base_agent";

export abstract class Agent extends BaseAgent {
    model: ReturnType<typeof createReactAgent>;

    config = {
        "configurable": {"thread_id": randomUUID()},
    }

    // TODO(class decorator here) @instrument("Agent.__init__", ["msn_str"])
    constructor(name: string, systemPrompt: string, tools: StructuredTool[]) {
        super(name, systemPrompt, tools);

        console.log(`Agent ${name} constructor`);
        const msn_str = getAgentMSN();
        const msn = MSN.from_string(msn_str);

        // a checkpointer + the thread_id below gives the model a way to save its
        // state so we don't have to accumulate the messages ourselves.
        const checkpointer = new MemorySaver();
        this.model = createReactAgent({
            llm: msn.constructModel(),
            tools: this.tools,
            checkpointSaver: checkpointer,
        });
        this.initialize();
    }

    initialize(): void {
    }

    preparePrompt(prompt: string): string {
        return prompt;
    }


    // TODO @instrument("Agent.runPrompt", ["prompt"])
    async runPrompt(prompt: string): Promise<string> {
        // TODO
        // logger = get_logger(__name__)
        // logger.info(f"Running prompt: {prompt}")

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
                messages:  [system, msg],
            },
            { 
                configurable: this.config.configurable,
                version: "v2",
            }
        )) {
            // console.log(JSON.stringify(event));
            const kind = event.event;

            if (kind != "on_chat_model_stream" && kind != "on_chain_end" && kind != "on_chain_stream" && kind != "on_chain_start") {
                // TODO logger.debug(f"[AGENT {self.name}] received event: {kind}")
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
                // const tool_name = event.name;
                // const tool_input = event.data.input;
                // logger.debug(f"tool start - name={tool_name}, input={repr(tool_input)}")
                continue;
            }

            if (kind == "on_tool_end") {
                // TODO
                // logger.debug("----")
                // const tool_name = event.name;
                // const tool_output = event.data.output.content[:20]
                // logger.debug(f"[AGENT {self.name}] tool end - name={tool_name}, output={repr(tool_output)}")
                continue;
            }

            if (kind == "on_chat_model_end") {
                if (Array.isArray(event.data.output["content"])) {
                    // anthropic seems give us content as a list?
                    result = event.data.output["content"][0]["text"];
                } else {
                    result = event.data.output.content;
                }
                console.log(`[AGENT ${this.name}] ${result}`);
                // TODO(toshok) still need to compute tokens
                continue;
            }

            if (kind == "on_custom_event") {
                // TODO(toshok) a better dispatch mechanism would be nice, but
                // there's only one event type currently
                if (event.name === "file_modified") {
                    modified_files.add(event.data);
                } else {
                    // TODO
                    // logger.debug(`[AGENT ${this.name}] Unknown prompt event: '${event["name"]}'`)
                }
                continue;
            }

        }

        await this.handleCompletion(modified_files);

        // TODO(toshok) we aren't returning a result here, and likely should...
        // TODO logger.debug(`[AGENT ${this.name}] runPrompt result: "${result || ""}"`)
        return result || "";
    }

    // TODO @instrument("Agent.handleCompletion")
    async handleCompletion(modified_files: Set<string>): Promise<void> {
        // TODO
        // current_span().set_attributes(
        //     {
        //         "num_modified_files": len(modified_files),
        //         "modified_files": str(modified_files),
        //     }
        // )

        let modified_file_promises: Promise<void>[] = [];
        modified_files.forEach(file => {
            modified_file_promises.push(this.handleModifiedFile(file));
        });
        await Promise.all(modified_file_promises);
    }

    // TODO @instrument("Agent.handle_modified_file", ["file"])
    async handleModifiedFile(file: string): Promise<void> {
        const original_file = path.join(getRootDir(), file);
        const modified_file = path.join(getArtifactsDir(), file);
        showDiff(original_file, modified_file);
        const response = (await askUser(
            `Do you want to apply the changes to ${file} (diff shown in VSCode)? (Y/n): `
        )).toLowerCase();

        const apply_changes = response == "y" || response == "";

        // TODO
        // current_span().set_attribute("apply_changes", apply_changes)

        if (apply_changes) {
            this.applyChanges(original_file, modified_file);
            console.log(`✅ Changes applied to ${file}`);
        } else {
            console.log(`❌ Changes not applied to ${file}`)
        }
    }

    // TODO @instrument("Agent.applyChanges", ["original_file", "modified_file"])
    applyChanges(original_file: string, modified_file: string): void {
        // TODO(toshok) we probably want the before/after size?  or something about size of the diff
        const modified_content = fs.readFileSync(modified_file, 'utf8');
        fs.writeFileSync(original_file, modified_content);
    }
}