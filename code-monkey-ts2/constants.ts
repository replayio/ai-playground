
let artifactsDir: string = "";
export function setArtifactsDir(dir: string): void {
  artifactsDir = dir;
}

export function getArtifactsDir(): string {
  return artifactsDir;
}

// Claude rate limit
export const CLAUDE_RATE_LIMIT = 40000; // tokens per minute
