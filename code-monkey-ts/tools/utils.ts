import * as fs from "fs";
import * as path from "path";
import { promisify } from "util";
import { getArtifactsDir } from "../constants";
import * as readline from "readline";
import { spawn } from "child_process";

const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);

export function getFileExtension(filename: string): string {
  return path.extname(filename).slice(1);
}

export function getFilenameWithoutExtension(filename: string): string {
  return path.basename(filename, path.extname(filename));
}

export async function readFileContent(filePath: string): Promise<string> {
  return await readFile(filePath, "utf-8");
}

export async function writeFileContent(
  filePath: string,
  content: string
): Promise<void> {
  await writeFile(filePath, content, "utf-8");
}

export function joinPaths(...paths: string[]): string {
  return path.join(...paths);
}

export function getAbsolutePath(relativePath: string): string {
  return path.resolve(relativePath);
}

export function getRelativePath(from: string, to: string): string {
  return path.relative(from, to);
}

export function fileExists(filePath: string): boolean {
  return fs.existsSync(filePath);
}

export function isDirectory(path: string): boolean {
  return fs.statSync(path).isDirectory();
}

export function createDirectory(dirPath: string): void {
  fs.mkdirSync(dirPath, { recursive: true });
}

export function listFiles(dirPath: string): string[] {
  return fs.readdirSync(dirPath);
}

export function makeFilePath(name: string): string {
  // resolve here because `name` could start with "../" and escape the
  // artifacts directory
  const filePath = path.resolve(getArtifactsDir(), name);
  if (!filePath.startsWith(getArtifactsDir())) {
    throw new Error(
      "Access to file outside artifacts directory is not allowed"
    );
  }
  return filePath;
}

export function askUser(prompt: string): Promise<string> {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  return new Promise((resolve) => {
    rl.question(prompt + "\n", (answer) => {
      rl.close();
      resolve(answer);
    });
  });
}

export function showDiff(originalFile: string, modifiedFile: string): void {
  console.debug(`Diffing ${originalFile} and ${modifiedFile}`);
  if (fs.existsSync(originalFile) && fs.existsSync(modifiedFile)) {
    spawn("code", ["--diff", originalFile, modifiedFile], { stdio: "inherit" });
  } else if (fs.existsSync(modifiedFile)) {
    spawn("code", [modifiedFile], { stdio: "inherit" });
  } else if (fs.existsSync(originalFile)) {
    console.log("File deleted.");
  } else {
    throw new Error(
      `Could not diff files. Neither file exists: ${originalFile} and ${modifiedFile}`
    );
  }
}