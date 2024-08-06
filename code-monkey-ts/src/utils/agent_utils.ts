import { BaseLanguageModel } from '@langchain/core/language_models/base';
import { Tool } from '@langchain/core/tools';
import { BaseMemory } from '@langchain/core/memory';
import { AgentExecutor, createReactAgent as createReactAgentLangchain } from '@langchain/core/agents';

export function createReactAgent(
  model: BaseLanguageModel,
  tools: Tool[],
  memory: BaseMemory
): AgentExecutor {
  // Create the ReAct agent using LangChain's function
  const agent = createReactAgentLangchain({
    llm: model,
    tools,
    verbose: true
  });

  // Create and return an AgentExecutor with the agent and memory
  return new AgentExecutor({
    agent,
    tools,
    memory,
    verbose: true
  });
}
