import boxen from "boxen";
import chalk from "chalk";

export function initPrettyLogging(): void {
  // Monkey patch console.debug
  const originalDebug = console.debug;
  if (process.env.NO_DEBUG) {
    // Mute debug messages.
    console.debug = (): void => {};
  } else {
    console.debug = (...args: any[]): void => {
      const formattedArgs = args.map((arg) =>
        // typeof arg === "string" ?  : arg
        typeof arg === "string"
          ? boxen(chalk.gray(arg), {
              /*backgroundColor: "greenBright",*/ dimBorder: true,
            })
          : arg
      );

      // Call the original debug function with the colored arguments
      return originalDebug.apply(console, formattedArgs);
    };
  }

  // Monkey patch console.log
  const originalLog = console.log;
  console.log = (...args: any[]): void => {
    const formattedArgs = args; // .map((arg) =>
    //   // typeof arg === "string" ?  : arg
    //   typeof arg === "string"
    //     ? boxen(arg, { /*backgroundColor: "greenBright",*/ dimBorder: false })
    //     : arg
    // )

    /**
     * Draw HR.
     * @see https://en.wikipedia.org/wiki/Box-drawing_characters.
     */
    originalLog("\u2501".repeat(100));
    // Call the original debug function with the colored arguments
    return originalLog.apply(console, formattedArgs);
  };
}
