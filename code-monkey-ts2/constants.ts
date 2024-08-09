import path from "path";

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

// Claude rate limit
export const CLAUDE_RATE_LIMIT = 40000;  // tokens per minute
