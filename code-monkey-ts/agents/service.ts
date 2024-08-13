import { CodeContext } from "../code_context";
import { Agent } from "./agent";
import { getAgentByName } from "./agents";
import { PromptResult } from "./base_agent";

class AgentService {
  agent: Agent;
  constructor(agent: Agent) {
    this.agent = agent;
  }

  async sendPrompt(prompt: string): Promise<PromptResult> {
    // console.debug(`Sending prompt to ${this.agent.name}: ${prompt}`);
    return await this.agent.runPrompt(prompt);
  }
}

const serviceByAgentName: Record<string, AgentService> = Object.create(null);
export async function getServiceForAgent(
  agentName: string,
  codeContext: CodeContext
): Promise<AgentService> {
  if (serviceByAgentName[agentName]) {
    return serviceByAgentName[agentName];
  }
  const AgentClass = getAgentByName(agentName);
  if (!AgentClass) {
    throw new Error(`Invalid agent invocation - Agent name does not exist: "${agentName}"`);
  }
  const agent = new AgentClass(codeContext);
  await agent.initialize();

  const service = new AgentService(agent);

  // TODO(toshok) commenting out the next line will cause us to reuse agents
  // across multiple prompts.  There's no real reason for it to be a problem
  // to reuse our agents, but since we don't have a unique thread_id for each
  // "conversation", it will be.
  //
  // serviceByAgentName[agentName] = service;
  return service;
}