import { z } from 'zod';
import { AsyncCallbackManagerForToolRun } from '@langchain/core/callbacks/manager';
import { tool } from '@langchain/core/tools';
import { CATool } from './CATool';
import { resolveFilePath, resolveModulePath } from '../deps';
import { instrument } from '../../instrumentation';

const CAASTAnalyzerToolInputSchema = z.object({
  files: z.array(z.string()).optional().describe("List of relative file paths to analyze"),
  modules: z.array(z.string()).optional().describe("List of modules to analyze")
}).refine(data => data.files != null || data.modules != null, {
  message: "Either 'files' or 'modules' must be provided"
});

type CAASTAnalyzerToolInput = z.infer<typeof CAASTAnalyzerToolInputSchema>;

export class CAASTAnalyzerTool extends CATool {
  name = "ca_analyze_ast";
  description = "Analyze the Abstract Syntax Tree of Python files";
  argsSchema = CAASTAnalyzerToolInputSchema;

  constructor() {
    super();
  }

  @instrument("Tool._run", ["files", "modules"], { attributes: { tool: "CAASTAnalyzerTool" } })
  async _run(
    input: CAASTAnalyzerToolInput,
    runManager?: AsyncCallbackManagerForToolRun,
  ): Promise<string> {
    const { files = [], modules = [] } = input;

    const allFiles = [
      ...files.map(resolveFilePath),
      ...modules.map(resolveModulePath)
    ];

    const summaries = await this.parser.summarizeModules(allFiles);

    return JSON.stringify(summaries, null, 1);
  }
}

export const caASTAnalyzerTool = tool({
  name: "ca_analyze_ast",
  description: "Analyze the Abstract Syntax Tree of Python files",
  schema: CAASTAnalyzerToolInputSchema,
  func: async (input: CAASTAnalyzerToolInput, runManager?: AsyncCallbackManagerForToolRun) => {
    const tool = new CAASTAnalyzerTool();
    return tool._run(input, runManager);
  }
});
