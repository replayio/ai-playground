import yaml from "yaml";
import { z } from "zod";
import * as fs from "fs";
import * as path from "path";

import { AgentsConfig } from "./types";

const AgentsSchema = z.object({
  agents: z.record(
    z.string(),
    z.object({
      msn: z.string(),
    }),
  ),
});

function loadYamlFile<T extends z.AnyZodObject>(
  path: string,
  schema: T,
): z.infer<T> {
  const contents = fs.readFileSync(path, "utf8");
  const parsedYaml = yaml.parse(contents);

  console.log(JSON.stringify(parsedYaml.agents, null, 2));

  return schema.parse({ agents: parsedYaml.agents });
}

export function loadAgentsConfig(): AgentsConfig {
  const config = loadYamlFile(
    path.resolve(__dirname, "agents.yml"),
    AgentsSchema,
  );
  const agentsConfig: AgentsConfig = {};

  for (const [key, value] of Object.entries(config.agents)) {
    agentsConfig[key] = value;
  }

  return agentsConfig;
}
