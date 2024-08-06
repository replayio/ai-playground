import * as fs from 'fs';
import * as path from 'path';
import * as shutil from 'fs-extra';
import ignore from 'ignore';
import { getArtifactsDir, getRootDir } from './src/constants';

function getAllSrcFiles(): string[] {
    const srcFiles: string[] = [];
    const rootDir: string = getRootDir();

    // Read .gitignore patterns
    let gitignorePatterns: string[] = [".git"];
    // Check current directory and up to max 3 parent directories until we hit
    // our root dir.
    for (let i = 0; i < 4; i++) {
        const dirPath: string = path.resolve(__dirname, ...Array(i).fill('..'));
        const gitignorePath: string = path.join(dirPath, ".gitignore");

        console.debug(`checking gitignore path ${gitignorePath}`);
        if (fs.existsSync(gitignorePath)) {
            console.debug("   found it");
            const gitignoreContent: string = fs.readFileSync(gitignorePath, 'utf-8');
            gitignorePatterns = gitignorePatterns.concat(gitignoreContent.split('\n'));
        }

        if (dirPath === rootDir) {
            break;
        }
    }

    // Create ignore object
    const ignoreSpec = ignore().add(gitignorePatterns);

    const walkSync = (dir: string, filelist: string[] = []): string[] => {
        fs.readdirSync(dir).forEach((file) => {
            const dirFile = path.join(dir, file);
            if (fs.statSync(dirFile).isDirectory()) {
                filelist = walkSync(dirFile, filelist);
            } else {
                const relPath = path.relative(getRootDir(), dirFile);
                if (!ignoreSpec.ignores(relPath)) {
                    filelist.push(relPath);
                }
            }
        });
        return filelist;
    };

    return walkSync(getRootDir());
}

export class CodeContext {
    private knownFiles: string[];

    constructor() {
        this.knownFiles = [];
    }

    copySrc(): string[] {
        const destDir: string = getArtifactsDir();

        if (!fs.existsSync(destDir)) {
            fs.mkdirSync(destDir, { recursive: true });
        }

        const filesToCopy: string[] = getAllSrcFiles();

        for (const relPath of filesToCopy) {
            const srcPath: string = path.join(getRootDir(), relPath);
            const destPath: string = path.join(destDir, relPath);
            fs.mkdirSync(path.dirname(destPath), { recursive: true });
            shutil.copySync(srcPath, destPath);
        }

        this.knownFiles = filesToCopy;
        return this.knownFiles;
    }
}

if (require.main === module) {
    for (const file of getAllSrcFiles()) {
        console.log(file);
    }
}
