// Placeholder for service module
interface AgentService {
    send_to: (data: { prompt: string }) => Promise<void>;
    receive_from: () => Promise<unknown>;
}

export const services_by_agent_name: Record<string, AgentService> = {};

// Add any other necessary exports or placeholder functions here
export function getAgentService(agentName: string): AgentService | null {
    return services_by_agent_name[agentName] || null;
}
