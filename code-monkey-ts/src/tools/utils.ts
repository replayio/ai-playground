import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';

const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);

export function getFileExtension(filename: string): string {
    return path.extname(filename).slice(1);
}

export function getFilenameWithoutExtension(filename: string): string {
    return path.basename(filename, path.extname(filename));
}

export async function readFileContent(filePath: string): Promise<string> {
    return await readFile(filePath, 'utf-8');
}

export async function writeFileContent(filePath: string, content: string): Promise<void> {
    await writeFile(filePath, content, 'utf-8');
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

// Main execution
if (require.main === module) {
    console.log('This module provides utility functions for file and path operations.');
    console.log('Import and use these functions in your TypeScript code as needed.');
}
