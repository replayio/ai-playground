import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import { exec } from 'child_process';
import { z } from 'zod';
import { StructuredTool, ToolParams } from '@langchain/core/tools';
import { CallbackManagerForToolRun } from '@langchain/core/callbacks/manager';
import { instrument } from '../instrumentation';

const writeFile = promisify(fs.writeFile);
const execAsync = promisify(exec);

const InvokeAgentSchema = z.object({
    agentName: z.string().describe("Name of the agent to invoke"),
    agentInput: z.string().describe("Input for the agent")
});

type InvokeAgentInput = z.infer<typeof InvokeAgentSchema>;

export class InvokeAgentTool extends StructuredTool<typeof InvokeAgentSchema> {
    name = "invoke_agent" as const;
    description = "Invokes another agent by name and runs it with a given input";
    schema = InvokeAgentSchema;

    constructor(fields?: Partial<ToolParams>) {
        super(fields);
    }

    protected async _call(
        input: InvokeAgentInput,
        runManager?: CallbackManagerForToolRun
    ): Promise<string> {
        const { agentName, agentInput } = input;
        try {
            // Write input to a temporary file
            const tempInputFile = path.join(__dirname, 'temp_input.txt');
            await writeFile(tempInputFile, agentInput, 'utf8');

            // Execute the agent
            const command = `python -m code_monkey.main ${agentName} ${tempInputFile}`;
            const { stdout, stderr } = await execAsync(command);

            // Clean up temporary file
            fs.unlinkSync(tempInputFile);

            if (stderr) {
                throw new Error(stderr);
            }

            return stdout.trim();
        } catch (error) {
            throw new Error(`Failed to invoke agent: ${(error as Error).message}`);
        }
    }
}

export const invokeAgentTool = new InvokeAgentTool();

// Instrumentation
// TODO: Re-enable instrumentation once type issues are resolved
// const instrumentedCall = instrument(
//   "Tool._call",
//   ["agentName", "agentInput"],
//   { attributes: { tool: "InvokeAgentTool" } }
// )(InvokeAgentTool.prototype._call);

// InvokeAgentTool.prototype._call = function(this: InvokeAgentTool, ...args: Parameters<typeof instrumentedCall>) {
//     return instrumentedCall.apply(this, args);
// };

// Main execution
if (require.main === module) {
    (async () => {
        if (process.argv.length !== 4) {
            console.error('Usage: ts-node invoke_agent_tool.ts <agent_name> <input>');
            process.exit(1);
        }

        const [, , agentName, agentInput] = process.argv;
        try {
            const result = await invokeAgentTool.call({
                agentName,
                agentInput
            });
            console.log('Agent output:');
            console.log(result);
        } catch (error) {
            console.error('Error:', (error as Error).message);
            process.exit(1);
        }
    })();
}
