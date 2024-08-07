import * as fs from 'fs';
import * as path from 'path';
import * as child_process from 'child_process';
import { tool } from "@langchain/core/tools";
import { z } from "zod";
import { getArtifactsDir } from '../constants';
import { instrument } from '../instrumentation';
import { makeFilePath } from './utils';

const summarizeProfilingOutput = (profFile: string): Record<string, any> => {
    const rv: Record<string, any> = {};

    const pstatsOutput = child_process.execSync(
        `python -c "import pstats; p = pstats.Stats('${profFile}'); p.sort_stats('cumulative').print_stats('/Users/toshok/src/replayio/ai-playground/code-monkey/src/.*.py')"`,
        { encoding: 'utf-8' }
    );

    const lines = pstatsOutput.split('\n').map(line => line.trim());

    let seenHeaders = false;
    for (const line of lines) {
        if (!seenHeaders) {
            if (line.startsWith('ncalls')) {
                seenHeaders = true;
            }
            continue;
        }

        const lineParts = line.split(/\s+/).filter(Boolean);
        if (lineParts.length !== 6) {
            continue;
        }

        const [ncalls, tottime, totpercall, cumtime, cumpercall, key] = lineParts;
        rv[key] = {
            ncalls: parseInt(ncalls, 10),
            tottime: parseFloat(tottime),
            totpercall: parseFloat(totpercall),
            cumtime: parseFloat(cumtime),
            cumpercall: parseFloat(cumpercall),
        };
    }

    return rv;
};

const schema = z.object({
    fname: z.string().describe("Name of the test file to run."),
});

export const runTestTool = tool(
    instrument("Tool._run", ["fname"], { attributes: { tool: "RunTestTool" } })(
        async ({ fname }: z.infer<typeof schema>) => {
            const tempFilePath = path.join(process.cwd(), 'profile.out');

            const filePath = makeFilePath(fname);

            if (!fs.existsSync(filePath)) {
                throw new Error(`The file ${fname} does not exist.`);
            }

            const testCommand = [
                'python',
                '-m',
                'cProfile',
                '-o',
                tempFilePath,
                '-m',
                'unittest',
                filePath,
            ];

            console.log(`Running test with command: ${testCommand.join(' ')}`);

            try {
                const result = child_process.spawnSync(testCommand[0], testCommand.slice(1), {
                    cwd: getArtifactsDir(),
                    encoding: 'utf-8',
                });

                const profilingData = summarizeProfilingOutput(tempFilePath);

                return `returncode=${result.status}\nstdout=${result.stdout}\nstderr=${result.stderr}\nprofiling=${JSON.stringify(profilingData)}`;
            } finally {
                if (fs.existsSync(tempFilePath)) {
                    fs.unlinkSync(tempFilePath);
                }
            }
        }
    ),
    {
        name: "run_test",
        description: "Run Python tests in a given file and return the results",
        schema: schema,
    }
);