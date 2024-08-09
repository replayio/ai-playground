import * as fs from "fs";
import * as path from "path";
import * as util from "util";
import { getArtifactsDir, getRootDir } from "./constants";
import { instrument } from "./instrumentation";

const readFile = util.promisify(fs.readFile);
const writeFile = util.promisify(fs.writeFile);
const mkdir = util.promisify(fs.mkdir);
const copyFile = util.promisify(fs.copyFile);

function patternToRegExp(pattern: string): RegExp {
  return new RegExp(
    pattern.replace(/\./g, "\\.").replace(/\*/g, ".*").replace(/\?/g, "."),
  );
}
class CodeContext {
  knownFiles: string[] = [];

  constructor(
    public rootDir: string,
    public artifactsDir?: string,
  ) {}

  @instrument("CodeContext.indexFiles")
  async indexFiles(): Promise<void> {
    // Get all files.
    const filesToCopy = await this.getAllSrcFiles(this.rootDir);
    console.log(`DDBG init ${filesToCopy}`);
    this.knownFiles = filesToCopy;

    // Copy files if a separate aritfactsDir is provided.
    if (this.artifactsDir) {
      if (!fs.existsSync(this.artifactsDir)) {
        await mkdir(this.artifactsDir, { recursive: true });
      }

      for (const relPath of filesToCopy) {
        const srcPath = path.join(this.rootDir, relPath);
        const destPath = path.join(this.artifactsDir, relPath);
        await mkdir(path.dirname(destPath), { recursive: true });
        await copyFile(srcPath, destPath);
      }
    }
  }

  @instrument("CodeContext.getAllSrcFiles")
  async getAllSrcFiles(rootDir = getRootDir()): Promise<string[]> {
    const srcFiles: string[] = [];

    // Build up a list of patterns to check against paths to skip.  start with
    // some defaults, then look for .gitignore files up from the current directory.
    let skipRegExps: RegExp[] = [patternToRegExp(".git/")];

    // Check current directory and up to max 3 parent directories until we hit our root dir
    for (let i = 0; i < 4; i++) {
      const dirPath = path.resolve(__dirname, ...Array(i).fill(".."));
      const gitignorePath = path.join(dirPath, ".gitignore");

      console.debug(`checking gitignore path ${gitignorePath}`);
      if (fs.existsSync(gitignorePath)) {
        console.debug("   found it");
        const gitignorePatterns = ((await readFile(gitignorePath, "utf-8")).split("\n").filter((l) => l.trim() !== ""));
        skipRegExps = skipRegExps.concat(gitignorePatterns.map(patternToRegExp));
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
        const relPath = path.relative(rootDir, filePath);
        if (
          skipRegExps.some((regex) => regex.test(relPath))
        ) {
          continue;
        }

        if (stat.isDirectory()) {
          walk(filePath);
        } else {
          srcFiles.push(relPath);
        }
      }
    };

    walk(rootDir);
    return srcFiles;
  }
}

// Main execution
if (require.main === module) {
  const codeContext = new CodeContext(getRootDir(), getArtifactsDir());
  (async (): Promise<void> => {
    const files = await codeContext.getAllSrcFiles();
    for (const file of files) {
      console.log(file);
    }
  })();
}

export { CodeContext };
