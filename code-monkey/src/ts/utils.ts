import * as readline from 'readline';
import * as fs from 'fs';
import { createTwoFilesPatch } from 'diff';
import chalk from 'chalk';

export async function askUser(question: string): Promise<string> {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer);
    });
  });
}

export async function showDiff(originalFile: string, modifiedFile: string): Promise<void> {
  const original = await fs.promises.readFile(originalFile, 'utf8');
  const modified = await fs.promises.readFile(modifiedFile, 'utf8');

  const differences = createTwoFilesPatch(originalFile, modifiedFile, original, modified);

  console.log(
    differences
      .split('\n')
      .map((line: string) => {
        if (line.startsWith('+')) {
          return chalk.green(line);
        }
        if (line.startsWith('-')) {
          return chalk.red(line);
        }
        return line;
      })
      .join('\n')
  );
}
