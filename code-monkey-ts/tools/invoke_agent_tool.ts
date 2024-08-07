import { z } from "zod";
import { tool } from "@langchain/core/tools";
import { CallbackManagerForToolRun } from "@langchain/core/callbacks";
import { instrument } from "../instrumentation";
import { getLogger } from "../utils/logger";
import { dispatchCustomEvent } from "../utils/agent_utils";

// Assuming these imports exist in TypeScript version
import { ServicesByAgentName } from "../agents/service";

const schema = z.object({
    agent_name: z.string().describe("Name of the agent to invoke"),
    prompt: z.string().describe("Prompt to run with the agent"),
});

export const invokeAgentTool = tool(
    async ({ agent_name, prompt }: z.infer<typeof schema>, runManager?: CallbackManagerForToolRun) => {
        const logger = getLogger(__filename);
        try {
            // Assuming allowed_agents is defined somewhere in your TypeScript code
            const allowed_agents = ["agent1", "agent2", "agent3"]; // Replace with actual allowed agents

            if (!allowed_agents.includes(agent_name)) {
                throw new Error(`Agent '${agent_name}' not found or not allowed.`);
            }

            const service = ServicesByAgentName[agent_name];

            // send a prompt, then wait for a response
            await service.sendTo({ prompt: prompt });

            const response = await service.receiveFrom();

            // emit a custom event with the response
            dispatchCustomEvent("agent_response", response);
            
            logger.debug(`[invoke_agent TOOL] Successfully invoked agent '${agent_name}' and received a response: ${JSON.stringify(response)}`);
            return `Successfully invoked agent '${agent_name}' and received a response: ${JSON.stringify(response)}`;
        } catch (err) {
            const error_message = `Failed to invoke agent '${agent_name}': ${err instanceof Error ? err.message : String(err)}`;
            logger.error(error_message);
            console.trace(err);
            return error_message;
        }
    },
    {
        name: "invoke_agent",
        description: "Invokes another agent by name and runs it with a given prompt",
        schema: schema,
    }
);

// Decorator for instrumentation
const instrumentedInvokeAgentTool = instrument(
    "Tool._run",
    ["agent_name", "prompt"],
    { attributes: { tool: "InvokeAgentInput" } }
)(invokeAgentTool);

export { instrumentedInvokeAgentTool as invokeAgentTool };