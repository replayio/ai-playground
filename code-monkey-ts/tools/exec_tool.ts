import { z } from "zod";
import { tool } from "@langchain/core/tools";
import { exec } from "child_process";
import * as path from "path";
import { askUserTool } from "./ask_user_tool";
import { getArtifactsDir } from "../constants";
import { getAllSrcFiles } from "../code_context";
import { instrument } from "../instrumentation";

// Set to store approved commands
const approvedCommands = new Set<string>();

const schema = z.object({
    command: z.string().describe("The command to execute."),
});

const executeCommand = async (command: string): Promise<string> => {
    return new Promise((resolve, reject) => {
        exec(command, (error, stdout, stderr) => {
            if (error) {
                reject(new Error(`Command execution failed with return code ${error.code}.\nCommand: ${command}\nStdout: ${stdout}\nStderr: ${stderr}`));
            } else {
                resolve(`stdout=${stdout}\nstderr=${stderr}`);
            }
        });
    });
};

export const execTool = tool(
    async ({ command }: z.infer<typeof schema>) => {
        const fileTree = await getAllSrcFiles();

        // Convert matching file names to absolute paths
        const commandParts = command.split(' ');
        for (let i = 0; i < commandParts.length; i++) {
            if (fileTree.includes(commandParts[i])) {
                commandParts[i] = path.join(getArtifactsDir(), commandParts[i]);
            }
        }

        const modifiedCommand = commandParts.join(' ');

        if (!approvedCommands.has(modifiedCommand)) {
            const confirmation = await askUserTool.call({ question: `Do you want to execute the following command? [Y/n]\n${modifiedCommand}` });
            if (confirmation.toLowerCase() !== "y" && confirmation !== "") {
                throw new Error("Command execution cancelled by user.");
            }
            approvedCommands.add(modifiedCommand);
        }

        try {
            return await instrument("Tool._run", ["command"], { tool: "ExecTool" }, () => executeCommand(modifiedCommand));
        } catch (error) {
            throw new Error(`${error}`);
        }
    },
    {
        name: "exec",
        description: "Execute a command in the terminal",
        schema: schema,
    }
);