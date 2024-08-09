import * as fs from "node:fs/promises";
import * as path from "path";
import { getArtifactsDir, getSrcDir } from "./constants";
import { instrument } from "./instrumentation";

function patternToRegExp(pattern: string): RegExp {
  return new RegExp(
    pattern.replace(/\./g, "\\.").replace(/\*/g, ".*").replace(/\?/g, ".")
  );
}

class CodeContext {
  knownFiles: string[] = [];
  private _indexFilesPromise: Promise<void> | null = null;
  private _indexingDone = false;

  constructor(public originalDir: string, public artifactsDir?: string) {}

  /**
   * The directory that contains the modified files.
   */
  get targetDir(): string {
    return this.artifactsDir || this.originalDir;
  }

  resolveFile(relativePath: string): string {
    if (!this._indexingDone) {
      // TODO: Consider making this async and lazily wait for it to finish.
      throw new Error(`Tried to call CodeContext.resolveFile before indexing has finished.`);
    }
    const absPath = path.resolve(this.targetDir, relativePath);
    if (!absPath.startsWith(this.targetDir)) {
      throw new Error(
        `Access to file outside artifacts directory is not allowed: "${absPath}"`
      );
    }
    return absPath;
  }

  async indexFiles(): Promise<void> {
    if (!this._indexFilesPromise && !this._indexingDone) {
      this._indexFilesPromise = this._indexFiles();
    }
    await this._indexFilesPromise;
  }

  @instrument("CodeContext._indexFiles")
  private async _indexFiles(): Promise<void> {
    // Get all files.
    const filesToCopy = await this.getAllSrcFiles();
    this.knownFiles = filesToCopy;

    // Copy files if a separate aritfactsDir is provided.
    if (this.artifactsDir) {
      await fs.mkdir(this.artifactsDir, { recursive: true });

      for (const relPath of filesToCopy) {
        const srcPath = path.join(this.originalDir, relPath);
        const destPath = path.join(this.artifactsDir, relPath);
        await fs.mkdir(path.dirname(destPath), { recursive: true });
        await fs.copyFile(srcPath, destPath);
      }
    }
    this._indexingDone = true;
    this._indexFilesPromise = null;
  }

  // ... other parts of the class ...

  private async readGitignore(gitignorePath: string): Promise<RegExp[]> {
    const gitignoreContent = await fs.readFile(gitignorePath, "utf-8");
    const gitignorePatterns = gitignoreContent
      .split("\n")
      .filter((l) => l.trim() !== "");
    return gitignorePatterns.map(patternToRegExp);
  }

  private async getGitignorePatterns(dirPath: string): Promise<RegExp[]> {
    const gitignorePath = path.join(dirPath, ".gitignore");
    try {
      await fs.access(gitignorePath, fs.constants.R_OK);
    } catch {
      // .gitignore file doesn't exist or is not readable
      return [];
    }
    return await this.readGitignore(gitignorePath);
  }

  @instrument("CodeContext.getAllSrcFiles")
  async getAllSrcFiles(): Promise<string[]> {
    const srcFiles: string[] = [];
    const srcDir = this.originalDir;

    // Start with default patterns
    let globalSkipRegExps: RegExp[] = [patternToRegExp(".git/")];

    // Check current directory and up to max 3 parent directories until we hit our root dir
    for (let i = 0; i < 4; i++) {
      const dirPath = path.resolve(srcDir, ...Array(i).fill(".."));
      const newPatterns = await this.getGitignorePatterns(dirPath);
      globalSkipRegExps = globalSkipRegExps.concat(newPatterns);

      if (dirPath === srcDir) {
        break;
      }
    }

    const dirWorklist: Array<{ dir: string; skipRegExps: RegExp[] }> = [
      { dir: srcDir, skipRegExps: globalSkipRegExps },
    ];

    while (dirWorklist.length > 0) {
      const { dir, skipRegExps } = dirWorklist.pop()!;
      const files = await fs.readdir(dir);

      for (const file of files) {
        const filePath = path.join(dir, file);
        const stat = await fs.stat(filePath);
        const relPath = path.relative(srcDir, filePath);

        if (skipRegExps.some((regex) => regex.test(relPath))) {
          continue;
        }

        if (stat.isDirectory()) {
          const newPatterns = await this.getGitignorePatterns(filePath);
          const newSkipRegExps = [...skipRegExps, ...newPatterns];
          dirWorklist.push({ dir: filePath, skipRegExps: newSkipRegExps });
        } else {
          srcFiles.push(relPath);
        }
      }
    }

    return srcFiles;
  }
}

// Main execution
if (require.main === module) {
  const codeContext = new CodeContext(getSrcDir(), getArtifactsDir());
  (async (): Promise<void> => {
    const files = await codeContext.getAllSrcFiles();
    for (const file of files) {
      console.log(file);
    }
  })();
}

export { CodeContext };
