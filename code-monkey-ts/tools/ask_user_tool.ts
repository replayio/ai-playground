import * as readline from 'readline';
import { tool } from "@langchain/core/tools";
import { z } from "zod";
import { instrument } from '../instrumentation/instrument';

const askUser = async (prompt: string): Promise<string> => {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    return new Promise((resolve) => {
        rl.question(prompt + ' ', (answer) => {
            rl.close();
            resolve(answer.trim());
        });
    });
};

const schema = z.object({
    prompt: z.string().describe("The prompt to show the user"),
});

export const askUserTool = tool(
    instrument(
        async ({ prompt }: z.infer<typeof schema>) => {
            return await askUser(prompt);
        },
        "Tool._run",
        ["prompt"],
        { attributes: { tool: "AskUserTool" } }
    ),
    {
        name: "ask_user",
        description: "Ask the user a question and return their response",
        schema: schema,
    }
);