import { tool } from "@langchain/core/tools";
import { z } from "zod";
import * as path from 'path';
import { DependencyGraph } from '../deps';
import { getArtifactsDir } from '../constants';
import { instrument } from '../instrumentation';

const schema = z.object({
    module_names: z.array(z.string()).describe("List of module names to get dependencies for"),
});

export const getDependenciesTool = tool(
    async ({ module_names }: z.infer<typeof schema>) => {
        const modulePaths = module_names.map(module => path.join(getArtifactsDir(), `${module}.ts`));
        const dependencyGraph = new DependencyGraph(modulePaths);
        const dependencies = Object.fromEntries(
            Object.entries(dependencyGraph.modules).map(([name, module]) => [
                name,
                module.dependencies.map(dep => dep.name)
            ])
        );
        return JSON.stringify(dependencies);
    },
    {
        name: "get_dependencies",
        description: "Get the dependency graph for one or more TypeScript modules",
        schema: schema,
    }
);

// Decorator for instrumentation
function instrumentDecorator(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;
    descriptor.value = function (...args: any[]) {
        return instrument("Tool._run", { tool: "GetDependenciesTool" }, () => {
            return originalMethod.apply(this, args);
        });
    };
    return descriptor;
}

// Apply the decorator to the tool function
instrumentDecorator(getDependenciesTool, 'handler', Object.getOwnPropertyDescriptor(getDependenciesTool, 'handler')!);