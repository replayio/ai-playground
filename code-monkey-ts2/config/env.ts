import dotenv from "dotenv";

export function loadEnvironment(): void {
  // Load environment variables from .env and .secret.env
  dotenv.config();
  dotenv.config({ path: ".env.secret" });
}

export function getAgentMSNEnvVar(agentName: string): string | undefined {
  return process.env[`${agentName.toUpperCase()}_MSN`];
}
