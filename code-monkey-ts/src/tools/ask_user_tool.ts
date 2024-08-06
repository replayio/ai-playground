import * as readline from 'readline';
import { z } from 'zod';
import { StructuredTool, ToolParams } from '@langchain/core/tools';
import { CallbackManagerForToolRun } from '@langchain/core/callbacks/manager';
import { instrument } from '../instrumentation';

const AskUserSchema = z.object({
    input: z.string().describe("The question to ask the user")
});

type AskUserInput = z.infer<typeof AskUserSchema>;

export class AskUserTool extends StructuredTool<typeof AskUserSchema> {
    name = "ask_user" as const;
    description = "Ask the user a question and return their response";
    schema = AskUserSchema;

    constructor(fields?: Partial<ToolParams>) {
        super(fields);
    }

    static lc_name() {
        return "AskUserTool";
    }

    async _call(
        { input: question }: AskUserInput,
        runManager?: CallbackManagerForToolRun
    ): Promise<string> {
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });

        return new Promise((resolve) => {
            rl.question(question + ' ', (answer) => {
                rl.close();
                resolve(answer.trim());
            });
        });
    }
}

export const askUserTool = new AskUserTool();

// Instrumentation is temporarily disabled due to type errors
// TODO: Re-enable instrumentation once type issues are resolved
// AskUserTool.prototype._call = instrument("Tool._call", ["input"], {
//   attributes: { tool: "AskUserTool" }
// })(AskUserTool.prototype._call);

// Main execution
if (require.main === module) {
    (async () => {
        if (process.argv.length !== 3) {
            console.error('Usage: ts-node ask_user_tool.ts "<question>"');
            process.exit(1);
        }

        const [, , question] = process.argv;
        try {
            const result = await askUserTool._call({ input: question });
            console.log('User response:', result);
        } catch (error) {
            console.error('Error:', (error as Error).message);
            process.exit(1);
        }
    })();
}
