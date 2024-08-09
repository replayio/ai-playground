import { initializeConfig } from "./config";
import { initializeTracer, shutdownTracer } from "./instrumentation";

export function initializeCodeMonkey(): void {
  initializeConfig();
  initializeTracer();
}

export async function shutdownCodeMonkey(): Promise<void> {
  await shutdownTracer();
}