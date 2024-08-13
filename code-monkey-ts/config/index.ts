import { loadAgentsConfig } from "./yaml";
import {
  getAgentMSNEnvVar,
  getDefaultAgentMSNEnvVar,
  loadEnvironment,
} from "./env";
import { AgentConfig, AgentsConfig } from "./types";

let agentsConfig: AgentsConfig;

export function initializeConfig(): void {
  loadEnvironment();
  agentsConfig = loadAgentsConfig();
}

export function getAgentConfig(agentName: string): AgentConfig {
  // environment variable overrides yaml
  loadEnvironment();
  const msn = getAgentMSNEnvVar(agentName);
  if (msn) {
    return { msn };
  }

  const agentConfig = agentsConfig[agentName];
  if (agentConfig) {
    return { msn: agentConfig.msn };
  }

  // there wasn't an agent specific one configured.
  // try loading "default", again with an env var overriding it.
  const defaultMsn = getDefaultAgentMSNEnvVar();
  if (defaultMsn) {
    return { msn: defaultMsn };
  }

  const defaultAgentConfig = agentsConfig["default"];
  if (defaultAgentConfig) {
    return { msn: defaultAgentConfig.msn };
  }

  throw new Error(`No agent config found for ${agentName}`);
}
