import process from "process";
import path from "path";
import dotenv from "dotenv";

function getSrcDir(): string {
    // presumably __dirname is absolute, but just to be consistent everywhere
    return path.resolve(__dirname);
}

export function getRootDir(): string {
    return path.resolve(getSrcDir(), "..");
}

export function getArtifactsDir(): string {
    return path.resolve(getRootDir(), "artifacts");
}

export function loadEnvironment(): void {
    // Load environment variables from .env and .secret.env
    dotenv.config();
    dotenv.config({ path: ".env.secret"});
}

export const DEFAULT_MSN = "anthropic/claude-3-5-sonnet-20240620/anthropic-beta=max-tokens-3-5-sonnet-2024-07-15";

export function getAgentMSN(): string {
    return process.env.AI_MSN || DEFAULT_MSN;
}

// Claude rate limit
export const CLAUDE_RATE_LIMIT = 40000;  // tokens per minute
