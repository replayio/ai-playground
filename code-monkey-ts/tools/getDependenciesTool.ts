import * as fs from 'fs';
import * as path from 'path';
import { z } from 'zod';
import { StructuredTool, ToolParams } from '@langchain/core/tools';
import { CallbackManagerForToolRun } from '@langchain/core/callbacks/manager';
import { DepGraph } from 'dependency-graph';

const GetDependenciesToolSchema = z.object({
  input: z.string().describe("A JSON string containing module_names array")
});

type GetDependenciesToolInput = z.infer<typeof GetDependenciesToolSchema>;

interface ModuleNames {
  module_names: string[];
}

export class GetDependenciesTool extends StructuredTool<typeof GetDependenciesToolSchema> {
  name = "get_dependencies" as const;
  description = "Get the dependency graph for one or more TypeScript modules" as const;
  schema = GetDependenciesToolSchema;

  constructor(fields?: Partial<ToolParams>) {
    super(fields);
  }

  async _call(
    input: GetDependenciesToolInput,
    runManager?: CallbackManagerForToolRun
  ): Promise<string> {
    const { input: jsonInput } = input;
    if (!jsonInput) {
      return "No input provided. Please provide a JSON string containing module_names array.";
    }

    let moduleNames: ModuleNames;
    try {
      moduleNames = JSON.parse(jsonInput) as ModuleNames;
    } catch (error) {
      return `Invalid JSON input: ${(error as Error).message}`;
    }

    const { module_names } = moduleNames;
    const artifactsDir = process.env.ARTIFACTS_DIR || path.join(__dirname, '..', '..', 'artifacts');
    const modulePaths = module_names.map((module: string) => path.join(artifactsDir, `${module}.ts`));

    const graph = new DepGraph<string>();

    for (const modulePath of modulePaths) {
      const moduleName = path.basename(modulePath, '.ts');
      graph.addNode(moduleName);

      try {
        const content = await fs.promises.readFile(modulePath, 'utf-8');
        const importLines = content.match(/^(?:import|from)\s+(\w+)/gm);

        if (importLines) {
          for (const line of importLines) {
            const match = line.match(/^(?:import|from)\s+(\w+)/);
            if (match) {
              const dependency = match[1];
              if (module_names.includes(dependency)) {
                graph.addDependency(moduleName, dependency);
              }
            }
          }
        }
      } catch (error) {
        console.error(`Error reading file ${modulePath}: ${(error as Error).message}`);
      }
    }

    const dependencies: Record<string, string[]> = Object.fromEntries(
      module_names.map((module: string) => [
        module,
        graph.dependenciesOf(module)
      ])
    );

    return JSON.stringify(dependencies, null, 2);
  }
}
