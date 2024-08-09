import fs from "fs";
import path from "path";
import chalk from "chalk";

import { Manager } from "./agents";
import { getRootDir } from "./constants";
import { /*instrument,*/ initializeTracer } from "./instrumentation";
import { initializeConfig } from "./config";
// TODO import { setup_logging } from "./util/logs";

// Monkey patch console.debug
const originalDebug = console.debug;
console.debug = (...args: any[]): void => {
  // Use chalk.gray() to color the output
  const grayArgs = args.map((arg) =>
    typeof arg === "string" ? chalk.gray(arg) : arg,
  );

  // Call the original debug function with the colored arguments
  return originalDebug.apply(console, grayArgs);
};

// TODO(toshok) decorators not available here :thumbs-down:
// @instrument("main")
async function main(debug: Boolean): Promise<void> {
  // TODO setup_logging(debug)
  console.log(chalk.green.bold("Welcome to the AI Playground!"));

  console.log(chalk.blue.bold("Running Manager agent..."));

  const agent = new Manager();
  await agent.initialize();

  // Read prompt from .prompt.md file
  const prompt = fs.readFileSync(
    path.join(getRootDir(), ".prompt.md"),
    "utf-8",
  );

  await agent.runPrompt(prompt);
  console.log(chalk.green.bold("DONE"));
}

if (require.main === module) {
  initializeConfig();

  initializeTracer();

  const args = process.argv.slice(2);
  const debug = args.includes("--debug");

  main(debug)
    .then(() => {
      process.exit(0);
    })
    .catch((error) => {
      console.error("An error occurred:", error);
      process.exit(1);
    });
}
