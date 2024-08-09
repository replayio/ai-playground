import fs from "fs";
import path from "path";
import chalk from "chalk";

import { Manager } from "./agents";
import { getArtifactsDir, getRootDir, getSrcDir } from "./constants";
import { instrument } from "./instrumentation";
import { initDebugLogging } from "./utils/logUtil";
import { CodeContext } from "./code_context";
import runAgentPrompt from "./agents/runAgentPrompt";
import { initializeCodeMonkey } from "./code-monkey";
// TODO import { setup_logging } from "./util/logs";

initDebugLogging();

let defaultCodeContext: CodeContext | null = null;
function getDefaultCodeContext(): CodeContext {
  if (!defaultCodeContext) {
    defaultCodeContext = new CodeContext(getSrcDir(), getArtifactsDir());
  }
  return defaultCodeContext;
}

class CLI {
  // TODO(toshok) decorators not available here :thumbs-down:
  @instrument("CLI.main")
  static async main(debug: Boolean): Promise<void> {
    // TODO setup_logging(debug)
    console.log(chalk.green.bold("Welcome to the AI Playground!"));
    console.log(chalk.blue.bold("Running Manager agent..."));

    // Read prompt from .prompt.md file
    const prompt = fs
      .readFileSync(path.join(getRootDir(), ".prompt.md"), "utf-8")
      .trim();

    const codeContext = getDefaultCodeContext();
    await runAgentPrompt(Manager, codeContext, prompt);
    console.log(chalk.green.bold("DONE"));
  }
}

if (require.main === module) {
  initializeCodeMonkey();

  const args = process.argv.slice(2);
  const debug = args.includes("--debug");

  CLI.main(debug)
    .then(() => {
      process.exit(0);
    })
    .catch((error) => {
      console.error("An error occurred:", error);
      process.exit(1);
    });
}
