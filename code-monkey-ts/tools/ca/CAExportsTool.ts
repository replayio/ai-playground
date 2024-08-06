import { z } from 'zod';
import { AsyncCallbackManagerForToolRun } from '@langchain/core/callbacks/manager';
import { tool } from '@langchain/core/tools';
import { CATool } from './ca_tool';
import { resolveFilePath, resolveModulePath, getModuleName } from '../deps';
import { instrument } from '../../instrumentation';

const CAExportsToolInputSchema = z.object({
    files: z.array(z.string()).nullable().describe("List of relative file paths to analyze"),
    modules: z.array(z.string()).nullable().describe("List of modules to analyze")
}).refine(data => data.files != null || data.modules != null, {
    message: "Either 'files' or 'modules' must be provided"
});

type CAExportsToolInput = z.infer<typeof CAExportsToolInputSchema>;

export class CAExportsTool extends CATool {
    name = "ca_analyze_exports";
    description = "Analyze the exports in Python files";

    constructor() {
        super();
    }

    @instrument("Tool._run", ["files", "modules"], { attributes: { tool: "CAExportsTool" } })
    async _run(
        input: CAExportsToolInput,
        runManager?: AsyncCallbackManagerForToolRun
    ): Promise<string> {
        const { files = [], modules = [] } = input;

        const allFiles = [
            ...files.map(resolveFilePath),
            ...modules.map(resolveModulePath)
        ];

        const exportsAnalysis: Record<string, unknown> = {};
        for (const filePath of allFiles) {
            const moduleName = getModuleName(filePath);
            exportsAnalysis[moduleName] = await this.parser.getExports(filePath);
        }

        return JSON.stringify(exportsAnalysis, null, 1);
    }
}

export const caExportsTool = tool({
    name: "ca_analyze_exports",
    description: "Analyze the exports in Python files",
    schema: CAExportsToolInputSchema,
    func: async (input: CAExportsToolInput, runManager?: AsyncCallbackManagerForToolRun) => {
        const tool = new CAExportsTool();
        return tool._run(input, runManager);
    }
});
