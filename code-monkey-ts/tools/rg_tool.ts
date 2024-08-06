import { spawn } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import { z } from 'zod';
import { CallbackManagerForToolRun } from '@langchain/core/callbacks/manager';
import { tool } from '@langchain/core/tools';
import { getArtifactsDir } from '../src/constants';
import { instrument } from '../instrumentation';

const RgToolInputSchema = z.object({
    pattern: z.string().describe("The pattern to search for.")
});

type RgToolInput = z.infer<typeof RgToolInputSchema>;

class RgTool {
    name = "rg";
    description = "Search for a pattern in files within the artifacts folder using ripgrep";

    async _run(
        { pattern }: RgToolInput,
        runManager?: CallbackManagerForToolRun
    ): Promise<string> {
        console.debug(`get_artifacts_dir(): ${getArtifactsDir()}`);
        return this._searchWithRg(pattern);
    }

    private async _searchWithRg(pattern: string): Promise<string> {
        const command = ["rg", "-i", "--no-heading", "--with-filename", "-r", pattern, "."];
        console.debug(`Current working directory: ${process.cwd()}`);
        console.debug(`Executing command: ${command.join(' ')}`);

        return new Promise<string>((resolve, reject) => {
            const rg = spawn('rg', command.slice(1), { cwd: getArtifactsDir() });
            let stdout = '';
            let stderr = '';

            rg.stdout.on('data', (data) => {
                stdout += data.toString();
            });

            rg.stderr.on('data', (data) => {
                stderr += data.toString();
            });

            rg.on('close', (code) => {
                console.debug(`Raw output: ${stdout}`);
                if (code === 0) {
                    resolve(stdout.trim() || "0 matches found.");
                } else if (code === 1) {
                    console.debug("No matches found");
                    resolve("0 matches found.");
                } else {
                    console.error(`Error occurred: ${stderr}`);
                    reject(new Error(`Error occurred: ${stderr}`));
                }
            });
        });
    }
}

export const rgTool = tool({
    name: "rg",
    description: "Search for a pattern in files within the artifacts folder using ripgrep",
    schema: RgToolInputSchema,
    func: async (input: RgToolInput, runManager?: CallbackManagerForToolRun) => {
        const tool = new RgTool();
        return tool._run(input, runManager);
    }
});
