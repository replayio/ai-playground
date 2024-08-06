declare module './constants' {
  export const SRC_DIR: string;
  export const IGNORE_PATTERNS: string[];
  export function getArtifactsDir(): string;
  export function getRootDir(): string;
  // Add other constants that are exported from the constants module
}
