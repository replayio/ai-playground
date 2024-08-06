import { z } from 'zod';
import { Tool, ToolParams } from '@langchain/core/tools';
import { CallbackManagerForToolRun } from '@langchain/core/callbacks/manager';
import { instrument } from '../instrumentation';
import { services_by_agent_name } from './service';

const InvokeAgentInputSchema = z.object({
    agent_name: z.string().describe("Name of the agent to invoke"),
    prompt: z.string().describe("Prompt to run with the agent")
});

type InvokeAgentInput = z.infer<typeof InvokeAgentInputSchema>;

interface InvokeAgentToolParams extends ToolParams {
    allowed_agents?: string[];
}

export class InvokeAgentTool extends Tool {
    name = "invoke_agent";
    description = "Invokes another agent by name and runs it with a given prompt";
    schema = InvokeAgentInputSchema;
    allowed_agents: string[];

    constructor(fields?: Partial<InvokeAgentToolParams>) {
        super(fields);
        this.allowed_agents = fields?.allowed_agents || [];
    }

    async _call(
        input: InvokeAgentInput,
        runManager?: CallbackManagerForToolRun
    ): Promise<string> {
        const { agent_name, prompt } = input;

        if (!this.allowed_agents.includes(agent_name)) {
            throw new Error(`Agent '${agent_name}' not found or not allowed.`);
        }

        const service = services_by_agent_name[agent_name];
        if (!service) {
            throw new Error(`Service for agent '${agent_name}' not found.`);
        }

        try {
            // send a prompt, then wait for a response
            await service.send_to({ prompt });
            const response = await service.receive_from();

            // emit a custom event with the response
            runManager?.handleToolEnd(JSON.stringify(response));

            return JSON.stringify(response);
        } catch (error) {
            console.error("Failed to invoke agent:", agent_name);
            console.error(error);
            throw error;
        }
    }
}

export const invokeAgentTool = new InvokeAgentTool();

// Apply the instrumentation decorator
InvokeAgentTool.prototype._call = instrument(
    "Tool._call",
    ["agent_name", "prompt"],
    { attributes: { tool: "InvokeAgentTool" } }
)(InvokeAgentTool.prototype._call) as typeof InvokeAgentTool.prototype._call;
