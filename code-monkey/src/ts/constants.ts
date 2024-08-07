import * as path from 'path';

export const ROOT_DIR = path.resolve(__dirname, '..', '..');
export const ARTIFACTS_DIR = path.join(ROOT_DIR, 'artifacts');

export const AGENT_MSN = process.env.AGENT_MSN || 'gpt-3.5-turbo';

export function getRootDir(): string {
    return ROOT_DIR;
}

export function getArtifactsDir(): string {
    return ARTIFACTS_DIR;
}

export function getAgentMsn(): string {
    return AGENT_MSN;
}
