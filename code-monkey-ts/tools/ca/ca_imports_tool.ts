import { z } from 'zod';
import { AsyncCallbackManagerForToolRun } from '@langchain/core/callbacks/manager';
import { tool } from '@langchain/core/tools';
import { CATool } from './ca_tool';
import { resolveFilePath, resolveModulePath, getModuleName } from '../deps';
import { instrument } from '../../instrumentation';

const CAImportsToolInputSchema = z.object({
    files: z.array(z.string()).nullable().describe("List of relative file paths to analyze"),
    modules: z.array(z.string()).nullable().describe("List of modules to analyze")
}).refine(data => data.files != null || data.modules != null, {
    message: "Either 'files' or 'modules' must be provided"
});

type CAImportsToolInput = z.infer<typeof CAImportsToolInputSchema>;

export class CAImportsTool extends CATool {
    name = "ca_analyze_imports";
    description = "Analyze the imports in Python files";

    constructor() {
        super();
    }

    @instrument("Tool._run", ["files", "modules"], { attributes: { tool: "CAImportsTool" } })
    async _run(
        input: CAImportsToolInput,
        runManager?: AsyncCallbackManagerForToolRun
    ): Promise<string> {
        const { files = [], modules = [] } = input;

        const allFiles = [
            ...files.map(resolveFilePath),
            ...modules.map(resolveModulePath)
        ];

        const importsAnalysis: Record<string, unknown> = {};
        for (const filePath of allFiles) {
            const moduleName = getModuleName(filePath);
            importsAnalysis[moduleName] = await this.parser.getImports(filePath);
        }

        return JSON.stringify(importsAnalysis, null, 1);
    }
}

export const caImportsTool = tool({
    name: "ca_analyze_imports",
    description: "Analyze the imports in Python files",
    schema: CAImportsToolInputSchema,
    func: async (input: CAImportsToolInput, runManager?: AsyncCallbackManagerForToolRun) => {
        const tool = new CAImportsTool();
        return tool._run(input, runManager);
    }
});
