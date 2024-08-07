import { BaseLanguageModel } from '@langchain/core/language_models/base';
import { Tool } from '@langchain/core/tools';
import { BaseMemory } from '@langchain/core/memory';
import { AgentExecutor, createReactAgent as createReactAgentLangchain } from 'langchain/agents';

export function createReactAgent(
  model: BaseLanguageModel,
  tools: Tool[],
  memory: BaseMemory
): AgentExecutor {
  // Create the ReAct agent using LangChain's function
  const agent = createReactAgentLangchain({
    llm: model,
    tools,
  });

  // Create and return an AgentExecutor with the agent and memory
  return AgentExecutor.fromAgentAndTools({
    agent,
    tools,
    memory,
    verbose: true
  });
}
