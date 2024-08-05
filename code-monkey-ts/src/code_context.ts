import * as fs from 'fs';
import * as path from 'path';
import * as util from 'util';
import { getArtifactsDir, getRootDir } from './constants';

const readFile = util.promisify(fs.readFile);
const writeFile = util.promisify(fs.writeFile);
const mkdir = util.promisify(fs.mkdir);
const copyFile = util.promisify(fs.copyFile);

// Simple implementation of gitignore-style pattern matching
function matchesGitIgnorePattern(filePath: string, pattern: string): boolean {
    const regexPattern = pattern
        .replace(/\./g, '\\.')
        .replace(/\*/g, '.*')
        .replace(/\?/g, '.');
    const regex = new RegExp(`^${regexPattern}$`);
    return regex.test(filePath);
}

async function getAllSrcFiles(): Promise<string[]> {
    const srcFiles: string[] = [];
    const rootDir = getRootDir();

    // Read .gitignore patterns
    let gitignorePatterns: string[] = ['.git'];

    // Check current directory and up to max 3 parent directories until we hit our root dir
    for (let i = 0; i < 4; i++) {
        const dirPath = path.resolve(__dirname, ...Array(i).fill('..'));
        const gitignorePath = path.join(dirPath, '.gitignore');

        console.debug(`checking gitignore path ${gitignorePath}`);
        if (fs.existsSync(gitignorePath)) {
            console.debug('   found it');
            const gitignoreContent = await readFile(gitignorePath, 'utf-8');
            gitignorePatterns = gitignorePatterns.concat(gitignoreContent.split('\n'));
        }

        if (dirPath === rootDir) {
            break;
        }
    }

    // Walk through the directory
    const walk = (dir: string): void => {
        const files = fs.readdirSync(dir);
        for (const file of files) {
            const filePath = path.join(dir, file);
            const stat = fs.statSync(filePath);
            if (stat.isDirectory()) {
                walk(filePath);
            } else {
                const relPath = path.relative(rootDir, filePath);
                if (!gitignorePatterns.some(pattern => matchesGitIgnorePattern(relPath, pattern))) {
                    srcFiles.push(relPath);
                }
            }
        }
    };

    walk(rootDir);
    return srcFiles;
}

class CodeContext {
    private knownFiles: string[] = [];

    async copySrc(): Promise<string[]> {
        const destDir = getArtifactsDir();

        if (!fs.existsSync(destDir)) {
            await mkdir(destDir, { recursive: true });
        }

        const filesToCopy = await getAllSrcFiles();

        for (const relPath of filesToCopy) {
            const srcPath = path.join(getRootDir(), relPath);
            const destPath = path.join(destDir, relPath);
            await mkdir(path.dirname(destPath), { recursive: true });
            await copyFile(srcPath, destPath);
        }

        this.knownFiles = filesToCopy;
        return this.knownFiles;
    }
}

// Main execution
if (require.main === module) {
    (async () => {
        const files = await getAllSrcFiles();
        for (const file of files) {
            console.log(file);
        }
    })();
}

export { CodeContext, getAllSrcFiles };
