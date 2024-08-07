import { z } from "zod";
import { tool } from "@langchain/core/tools";
import { exec } from "child_process";
import { promisify } from "util";
import { getArtifactsDir } from "../constants";
import { instrument } from "../instrumentation";

const execAsync = promisify(exec);

const schema = z.object({
    pattern: z.string().describe("The pattern to search for."),
});

const searchWithRg = async (pattern: string): Promise<string> => {
    const command = `rg -i --no-heading --with-filename -r "${pattern}" .`;
    console.debug(`Current working directory: ${process.cwd()}`);
    console.debug(`Executing command: ${command}`);

    try {
        const { stdout } = await execAsync(command, { cwd: getArtifactsDir() });
        console.debug(`Raw output: ${stdout}`);

        if (stdout.trim()) {
            return stdout.trim();
        } else {
            return "0 matches found.";
        }
    } catch (error) {
        if (error.code === 1) { // No matches
            console.debug("No matches found");
            return "0 matches found.";
        } else {
            console.error(`Error occurred: ${error.message}`);
            throw new Error(`Error occurred: ${error.message}`);
        }
    }
};

export const rgTool = tool(
    instrument("Tool._run", ["pattern"], { tool: "RgTool" })(
        async ({ pattern }: z.infer<typeof schema>) => {
            console.debug(`getArtifactsDir(): ${getArtifactsDir()}`);
            return await searchWithRg(pattern);
        }
    ),
    {
        name: "rg",
        description: "Search for a pattern in files within the artifacts folder using ripgrep",
        schema: schema,
    }
);