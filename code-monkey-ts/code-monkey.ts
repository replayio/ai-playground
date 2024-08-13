import { initializeConfig } from "./config";
import { initializeTracer, shutdownTracer } from "./instrumentation";
import { initPrettyLogging } from "./utils/logUtil";

export function initializeCodeMonkey(): void {
  initPrettyLogging();
  initializeConfig();
  initializeTracer();
}

export async function shutdownCodeMonkey(): Promise<void> {
  await shutdownTracer();
}
