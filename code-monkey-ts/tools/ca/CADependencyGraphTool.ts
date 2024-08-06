import { z } from 'zod';
import { AsyncCallbackManagerForToolRun } from '@langchain/core/callbacks/manager';
import { tool } from '@langchain/core/tools';
import { CATool } from './CATool';
import { resolveFilePath, resolveModulePath, getModuleName } from '../deps';
import { instrument } from '../../instrumentation';
import { createGraph } from 'ngraph.graph';

const CADependencyGraphToolInputSchema = z.object({
  files: z.array(z.string()).optional().describe("List of relative file paths to analyze"),
  modules: z.array(z.string()).optional().describe("List of modules to analyze")
}).refine(data => data.files != null || data.modules != null, {
  message: "Either 'files' or 'modules' must be provided"
});

type CADependencyGraphToolInput = z.infer<typeof CADependencyGraphToolInputSchema>;

export class CADependencyGraphTool extends CATool {
  name = "ca_generate_dependency_graph";
  description = "Generate a dependency graph for Python files";
  argsSchema = CADependencyGraphToolInputSchema;

  constructor() {
    super();
  }

  @instrument("Tool._run", ["files", "modules"], { attributes: { tool: "CADependencyGraphTool" } })
  async _run(
    input: CADependencyGraphToolInput,
    runManager?: AsyncCallbackManagerForToolRun,
  ): Promise<string> {
    const { files = [], modules = [] } = input;

    const allFiles = [
      ...files.map(resolveFilePath),
      ...modules.map(resolveModulePath)
    ];

    const graph = createGraph();

    for (const filePath of allFiles) {
      const moduleName = getModuleName(filePath);
      const imports = await this.parser.getImports(filePath);

      for (const imp of imports) {
        graph.addLink(moduleName, imp);
      }
    }

    return JSON.stringify(graph, null, 1);
  }
}

export const caDependencyGraphTool = tool({
  name: "ca_generate_dependency_graph",
  description: "Generate a dependency graph for Python files",
  schema: CADependencyGraphToolInputSchema,
  func: async (input: CADependencyGraphToolInput, runManager?: AsyncCallbackManagerForToolRun) => {
    const tool = new CADependencyGraphTool();
    return tool._run(input, runManager);
  }
});
