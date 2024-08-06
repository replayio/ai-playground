declare module 'agents/agents' {
  export class Coder {
    // Add any known properties or methods of the Coder class
  }

  export class Manager {
    initialize(): void;
    runPrompt(prompt: string): Promise<void>;
  }

  export class CodeAnalyst {
    // Add any known properties or methods of the CodeAnalyst class
  }

  export function runAgentMain(agentClass: new () => any): Promise<void>;
}
