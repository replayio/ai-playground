#!/usr/bin/env tsx
import fs from "node:fs/promises";
import path from "path";
import chalk from "chalk";
import tmp from "tmp";
import { Command } from "commander";

import { name, version } from "../package.json";
import { instrument } from "./instrumentation";
import { setArtifactsDir } from "./constants";
import { CodeContext } from "./code_context";
import runAgentPrompt from "./agents/runAgentPrompt";
import { initializeCodeMonkey, shutdownCodeMonkey } from "./code-monkey";

const projectRootSignifiers = [
  "package.json",
  "pyproject.toml",
  "go.mod",
  "Cargo.toml",
  ".git",
];

export async function findProjectRoot(): Promise<string> {
  let currentDir = process.cwd();
  while (true) {
    const files = await fs.readdir(currentDir);
    if (files.some((file) => projectRootSignifiers.includes(file))) {
      return currentDir;
    }

    const parentDir = path.dirname(currentDir);
    if (parentDir === currentDir) {
      throw new Error("Failed to find project root.");
    }

    currentDir = parentDir;
  }
}

type Options = {
  debug: boolean | undefined;
  root?: string | undefined;
};

class CLI {
  static async run(): Promise<void> {
    initializeCodeMonkey();
    const program = new Command();

    program
      .name(name)
      .version(version);

    program
      .command("run", { isDefault: true })
      .option(
        "-r, --root <root project directory>",
        "specify the root of the source tree to use"
      )
      .option("-d, --debug", "show debug output")
      .action(CLI.main);

    program.exitOverride();

    let exitStatus = 0;
    try {
      await program.parseAsync(process.argv);
    } catch (e) {
      console.error("As error occurred:", e);
      exitStatus = 1;
    } finally {
      await shutdownCodeMonkey();
      process.exit(exitStatus);
    }
  }

  @instrument("CLI.main")
  static async main(options: Options): Promise<void> {
    const { Manager } = await import("./agents");
    // TODO setup_logging(debug)
    console.log(chalk.green.bold("Welcome to the AI Playground!"));
    console.log(chalk.blue.bold("Running Manager agent..."));

    const artifactsDir = tmp.dirSync();
    const projectRoot = options.root ?? await findProjectRoot();
    console.log(`Project root: ${projectRoot}`);
    console.log(`Artifacts dir: ${artifactsDir.name}`);

    setArtifactsDir(artifactsDir.name);

    // Read prompt from .prompt.md file
    const prompt = (
      await fs.readFile(path.join(projectRoot, ".prompt.md"), {
        encoding: "utf-8",
      })
    ).trim();

    const codeContext = new CodeContext(projectRoot, artifactsDir.name);
    await runAgentPrompt(Manager, codeContext, prompt);
    console.log(chalk.green.bold("DONE"));
  }
}

if (require.main === module) {
  CLI.run();
}
