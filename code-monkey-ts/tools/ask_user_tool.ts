import * as readline from 'readline';
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const askUser = async (question: string): Promise<string> => {
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
};

const schema = z.object({
    question: z.string().describe("The question to ask the user"),
});

export const askUserTool = tool(
    async ({ question }: z.infer<typeof schema>) => {
        return await askUser(question);
    },
    {
        name: "ask_user",
        description: "Ask the user a question and return their response",
        schema: schema,
    }
);
