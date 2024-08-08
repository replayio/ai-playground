import { z } from "zod";
import { StructuredTool } from "@langchain/core/tools";
import { dispatchCustomEvent } from "@langchain/core/callbacks/dispatch";
// TODO import { instrument } from "../instrumentation";
// TODO import { getLogger } from "../utils/logger";

import { getServiceForAgent } from "../agents";

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

    // TODO @instrument("Tool._call", ["agent_name", "prompt"], { tool: "InvokeAgentTool" })
    async _call({ agent_name, prompt }: z.infer<typeof schema>): Promise<string> {
        try {
            if (!this.allowedAgents.includes(agent_name)) {
                throw new Error(`Agent '${agent_name}' not found or not allowed.`);
            }

            const service = getServiceForAgent(agent_name);

            console.log(1);
            const response = await service.sendPrompt(prompt);
            console.log(2);

            // emit a custom event with the response
            // await dispatchCustomEvent("agent_response", response);
            
            // getLogger(__filename).debug(`[invoke_agent TOOL] Successfully invoked agent '${agent_name}' and received a response: ${JSON.stringify(response)}`);
            console.log(`[invoke_agent TOOL] Successfully invoked agent '${agent_name}' and received a response: ${JSON.stringify(response)}`);
            return response;
        } catch (err) {
            const error_message = `Failed to invoke agent '${agent_name}': ${err instanceof Error ? err.message : String(err)}`;
            // logger.error(error_message);
            console.trace(err);
            return error_message;
        }
    }

}