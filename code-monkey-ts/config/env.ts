import dotenv from "dotenv";
import path from "path";

export function loadEnvironment(): void {
  // Load environment variables from .env and .secret.env
  dotenv.config({ path: path.join(__dirname, "../../.env") });
  const secretPath = path.join(__dirname, "../../.env.secret");
  if (!dotenv.config({ path: secretPath })) {
    throw new Error(`loadEnvironment failed - secret file not found at "${secretPath}"`);
  }
}

export function getAgentMSNEnvVar(agentName: string): string | undefined {
  return process.env[`${agentName.toUpperCase()}_MSN`];
}

export function getDefaultAgentMSNEnvVar(): string | undefined {
  return process.env.AI_MSN || process.env.DEFAULT_MSN;
}
