import { initializeConfig } from "./config";
import { initializeTracer } from "./instrumentation";

export function initializeCodeMonkey(): void {
  initializeConfig();
  initializeTracer();
}
