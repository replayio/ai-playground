import fs from "fs";
import path from "path";
import chalk from "chalk";

import { Manager } from "./agents";
import { loadEnvironment, getRootDir } from "./constants";
// TODO import { instrument, initialize_tracers } from "./instrumentation";
// TODO import { setup_logging } from "./util/logs";

// TODO @instrument("main")
async function main(debug: Boolean): Promise<void> {
    // TODO setup_logging(debug)
    console.log(chalk.green.bold("Welcome to the AI Playground!"))

    console.log(chalk.blue.bold("Running Manager agent..."))

    const agent = new Manager();
    agent.initialize();

    // Read prompt from .prompt.md file
    const prompt = fs.readFileSync(path.join(getRootDir(), ".prompt.md"), "utf-8");

    await agent.runPrompt(prompt);
    console.log(chalk.green.bold("DONE"));
}

if (require.main === module) {
    loadEnvironment()

    // TODO
    // initialize_tracer(
    //     {
    //         "agent": "Manager",
    //     }
    // )

    const args = process.argv.slice(2);
    const debug = args.includes('--debug');

    main(debug).then(() => {
        process.exit(0);
    }).catch((error) => {
        console.error('An error occurred:', error);
        process.exit(1);
    });
}