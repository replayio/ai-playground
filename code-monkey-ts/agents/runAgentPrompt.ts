import { CodeContext } from "../code_context";
import { AgentConstructor } from "./agent";
import { PromptResult } from "./base_agent";

export default async function runAgentPrompt(
  AgentCtor: AgentConstructor,
  codeContext: CodeContext,
  prompt: string
): Promise<PromptResult> {
  const agent = new AgentCtor(codeContext);
  await agent.initialize();
  return await agent.runPrompt(prompt);
}
