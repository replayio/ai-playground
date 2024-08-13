import { z } from "zod";
import { StructuredTool } from "@langchain/core/tools";
import { instrument, currentSpan } from "../instrumentation";
// TODO import { getLogger } from "../utils/logger";

import { getServiceForAgent } from "../agents";
import { AsyncLocalStorage } from "async_hooks";
import { CodeContext } from "../code_context";

const schema = z.object({
  agent_name: z.string().describe("Name of the agent to invoke"),
  prompt: z.string().describe("Prompt to run with the agent"),
});

// a hack to clear the async local storage langchain uses to send events to the correct stream.
// this lets us run multiple agents with their own independent streamEvents loop.
const TRACING_ALS_KEY = Symbol.for("ls:tracing_async_local_storage");
function exitLangChainAsyncLocalStorage<T>(f: () => T): T {
  const storage: AsyncLocalStorage<any> = (globalThis as any)[
    TRACING_ALS_KEY
  ] as AsyncLocalStorage<any>;
  if (storage) {
    return storage.exit(f);
  } else {
    return f();
  }
}
export class InvokeAgentTool extends StructuredTool {
  name = "invoke_agent";
  schema = schema;
  description: string; // filled in dynamically in the constructor

  allowedAgents: string[];
  codeContext: CodeContext;

  constructor(allowedAgents: string[], codeContext: CodeContext) {
    super();
    this.allowedAgents = allowedAgents.slice();
    this.description = `Invokes another agent by name and runs it with a given prompt. Allowed agents: ${this.allowedAgents.join(
      ", "
    )}`;
    this.codeContext = codeContext;
  }

  @instrument("Tool._call", { attributes: { tool: "InvokeAgentTool" } })
  async _call({ agent_name, prompt }: z.infer<typeof schema>): Promise<string> {
    currentSpan().setAttributes({
      agent_name,
      prompt,
    });

    try {
      if (!this.allowedAgents.includes(agent_name)) {
        throw new Error(`[Agent '${agent_name}'] not found or not allowed.`);
      }

      const service = await getServiceForAgent(agent_name, this.codeContext);

      const response = await exitLangChainAsyncLocalStorage(() => {
        return service.sendPrompt(prompt);
      });

      // getLogger(__filename).debug(`[invoke_agent TOOL] Successfully invoked agent '${agent_name}' and received a response: ${JSON.stringify(response)}`);
      console.debug(
        `[invoke_agent TOOL] Successfully invoked agent '${agent_name}' and received a response: "${JSON.stringify(
          response.trim()
        )}"`
      );
      return response;
    } catch (err: any) {
      const error_message = `Failed to invoke agent '${agent_name}': ${
        err instanceof Error ? err.message : String(err)
      }`;
      // logger.error(error_message);
      console.error(err.stack);
      return error_message;
    }
  }
}
