import boxen from "boxen";
import chalk from "chalk";

const originalDebug = console.debug;
// Monkey patch console.debug
export function initDebugLogging(): void {
  console.debug = (...args: any[]): void => {
    // Use chalk.gray() to color the output
    const formattedArgs = args.map((arg) =>
      // typeof arg === "string" ?  : arg
      typeof arg === "string" ? boxen(chalk.black(arg), { backgroundColor: "blueBright", dimBorder: true }) : arg
    );

    // Call the original debug function with the colored arguments
    return originalDebug.apply(console, formattedArgs);
  };
}
