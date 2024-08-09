import { loadAgentsConfig } from "./yaml";
import { getAgentMSNEnvVar, loadEnvironment } from "./env";
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

    if (!agentConfig) {
        // try loading "default"
        const defaultAgentConfig = agentsConfig["default"];
        if (!defaultAgentConfig) {
            throw new Error(`No agent config found for ${agentName}`);
        }

        return { msn: defaultAgentConfig.msn };
    }

    return { msn: agentConfig.msn };
}