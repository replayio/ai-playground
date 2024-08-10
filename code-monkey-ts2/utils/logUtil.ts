import boxen from "boxen";
import chalk from "chalk";

export function initPrettyLogging(): void {
  // Monkey patch console.debug
  const originalDebug = console.debug;
  console.debug = (...args: any[]): void => {
    const formattedArgs = args.map((arg) =>
      // typeof arg === "string" ?  : arg
      typeof arg === "string" ? boxen(chalk.gray(arg), { /*backgroundColor: "greenBright",*/ dimBorder: true }) : arg
    );

    // Call the original debug function with the colored arguments
    return originalDebug.apply(console, formattedArgs);
  };

  // Monkey patch console.log
  const originalLog = console.log;
  console.log = (...args: any[]): void => {
    const formattedArgs = args.map((arg) =>
      // typeof arg === "string" ?  : arg
      typeof arg === "string" ? boxen(arg, { /*backgroundColor: "greenBright",*/ dimBorder: false }) : arg
    );

    // Call the original debug function with the colored arguments
    return originalLog.apply(console, formattedArgs);
  };
}
