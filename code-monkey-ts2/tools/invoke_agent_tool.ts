import { z } from "zod";
import { StructuredTool } from "@langchain/core/tools";
import { instrument, currentSpan } from "../instrumentation";
// TODO import { getLogger } from "../utils/logger";

import { getServiceForAgent } from "../agents";
import { AsyncLocalStorage } from "async_hooks";

const schema = z.object({
    agent_name: z.string().describe("Name of the agent to invoke"),
    prompt: z.string().describe("Prompt to run with the agent"),
});

export class InvokeAgentTool extends StructuredTool {
    name = "invoke_agent";
    schema = schema;
    description: string; // filled in dynamically in the constructor

    allowedAgents: string[];

    constructor(allowedAgents: string[]) {
        super();
        this.allowedAgents = allowedAgents.slice();
        this.description = `Invokes another agent by name and runs it with a given prompt. Allowed agents: ${this.allowedAgents.join(", ")}`;
    }

    @instrument("Tool._call", { tool: "InvokeAgentTool" })
    async _call({ agent_name, prompt }: z.infer<typeof schema>): Promise<string> {
        currentSpan().setAttributes({
            agent_name,
            prompt,
        });

        try {
            if (!this.allowedAgents.includes(agent_name)) {
                throw new Error(`Agent '${agent_name}' not found or not allowed.`);
            }

            const service = await getServiceForAgent(agent_name);

            const TRACING_ALS_KEY = Symbol.for("ls:tracing_async_local_storage");

            let response: string;

            const storage: AsyncLocalStorage<any> = globalThis[TRACING_ALS_KEY] as AsyncLocalStorage<any>;
            if (storage) {
                console.log("******* YESSSSS");
                response = await storage.exit(async () => {
                    return await service.sendPrompt(prompt);
                });
            } else {
                console.log("******* NOOOOOO");
                response = await service.sendPrompt(prompt);
            }

            // getLogger(__filename).debug(`[invoke_agent TOOL] Successfully invoked agent '${agent_name}' and received a response: ${JSON.stringify(response)}`);
            console.debug(`[invoke_agent TOOL] Successfully invoked agent '${agent_name}' and received a response: ${JSON.stringify(response)}`);
            return response;
        } catch (err) {
            const error_message = `Failed to invoke agent '${agent_name}': ${err instanceof Error ? err.message : String(err)}`;
            // logger.error(error_message);
            console.trace(err);
            return error_message;
        }
    }

}