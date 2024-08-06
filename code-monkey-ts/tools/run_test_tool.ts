import * as fs from 'fs/promises';
import * as path from 'path';
import * as os from 'os';
import { spawn } from 'child_process';
import { z } from 'zod';
import { CallbackManagerForToolRun } from '@langchain/core/callbacks/manager';
import { Tool, ToolParams } from '@langchain/core/tools';
import { instrument } from '../instrumentation';

const RunTestToolInputSchema = z.object({
  test_file: z.string().describe("The path to the test file to run"),
  profile: z.boolean().optional().describe("Whether to run the test with profiling")
});

type RunTestToolInput = z.infer<typeof RunTestToolInputSchema>;

interface TestResult {
  output: string;
  error: string | null;
  returncode: number;
}

class RunTestTool extends Tool {
  name = "run_test";
  description = "Run a TypeScript test file and return the results";
  schema = RunTestToolInputSchema;

  constructor(fields?: Partial<ToolParams>) {
    super({ ...fields, name: "run_test" });
  }

  private async cleanup(tempFiles: string[]): Promise<void> {
    for (const file of tempFiles) {
      try {
        await fs.unlink(file);
      } catch (error) {
        console.error(`Error deleting temporary file ${file}:`, error);
      }
    }
  }

  private async runTestWithProfiling(testFile: string): Promise<TestResult> {
    const tempProfileFile = path.join(os.tmpdir(), `profile_${Date.now()}.txt`);
    const command = `ts-node --prof ${testFile} > ${tempProfileFile}`;

    try {
      const result = await this.runCommand(command);
      const profileOutput = await this.summarizeProfilingOutput(tempProfileFile);
      return {
        ...result,
        output: `${result.output}\n\nProfiling Summary:\n${profileOutput}`
      };
    } finally {
      await this.cleanup([tempProfileFile]);
    }
  }

  private async summarizeProfilingOutput(profileFile: string): Promise<string> {
    const command = `node --prof-process ${profileFile}`;
    const result = await this.runCommand(command);
    return result.output;
  }

  private runCommand(command: string): Promise<TestResult> {
    return new Promise((resolve) => {
      const process = spawn(command, { shell: true });
      let output = '';
      let error = '';

      process.stdout.on('data', (data: Buffer) => {
        output += data.toString();
      });

      process.stderr.on('data', (data: Buffer) => {
        error += data.toString();
      });

      process.on('close', (code: number | null) => {
        resolve({
          output,
          error: error || null,
          returncode: code ?? 0
        });
      });
    });
  }

  async _call(
    { test_file, profile = false }: RunTestToolInput,
    runManager?: CallbackManagerForToolRun
  ): Promise<string> {
    try {
      const result = profile
        ? await this.runTestWithProfiling(test_file)
        : await this.runCommand(`ts-node ${test_file}`);

      return JSON.stringify({
        output: result.output,
        error: result.error,
        returncode: result.returncode
      });
    } catch (error) {
      console.error("Error running test:", error);
      throw error;
    }
  }
}

export const runTestTool = new RunTestTool();

// Wrapper function to apply the instrumentation decorator
export const instrumentedRunTestTool = instrument("Tool.call", ["test_file", "profile"], {
  attributes: { tool: "RunTestTool" }
})((input: RunTestToolInput, runManager?: CallbackManagerForToolRun) =>
  runTestTool._call(input, runManager)
);

// You can use the instrumented version like this:
// runTestTool._call = instrumentedRunTestTool;
