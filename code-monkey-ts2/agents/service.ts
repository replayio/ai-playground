import { Agent } from "./agent";
import { agentsByName } from './agents';

class AgentService {
    agent: Agent;
    constructor(agent: Agent) {
        this.agent = agent;
    }

    async sendPrompt(prompt: string): Promise<string> {
        console.log(`Sending prompt to ${this.agent.name}: ${prompt}`);
        return await this.agent.runPrompt(prompt);
    }
}


const serviceByAgentName: Record<string, AgentService> = Object.create(null);
export function getServiceForAgent(agentName: string): AgentService {
    if (serviceByAgentName[agentName]) {
        return serviceByAgentName[agentName];
    }
    const AgentClass = agentsByName[agentName];
    const agent = new AgentClass();
    agent.initialize();

    const service = new AgentService(agent);
    serviceByAgentName[agentName] = service;
    return service;
}