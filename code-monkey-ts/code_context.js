"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.CodeContext = void 0;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const shutil = __importStar(require("fs-extra"));
const pathspec = __importStar(require("pathspec"));
const constants_1 = require("./constants");
function getAllSrcFiles() {
    const srcFiles = [];
    const rootDir = (0, constants_1.getRootDir)();
    // Read .gitignore patterns
    let gitignorePatterns = [".git"];
    // Check current directory and up to max 3 parent directories until we hit
    // our root dir.
    for (let i = 0; i < 4; i++) {
        const dirPath = path.resolve(__dirname, ...Array(i).fill('..'));
        const gitignorePath = path.join(dirPath, ".gitignore");
        console.debug(`checking gitignore path ${gitignorePath}`);
        if (fs.existsSync(gitignorePath)) {
            console.debug("   found it");
            const gitignoreContent = fs.readFileSync(gitignorePath, 'utf-8');
            gitignorePatterns = gitignorePatterns.concat(gitignoreContent.split('\n'));
        }
        if (dirPath === rootDir) {
            break;
        }
    }
    // Create PathSpec object
    const ignoreSpec = pathspec.GitIgnoreSpec.from_lines(gitignorePatterns);
    const walkSync = (dir, filelist = []) => {
        fs.readdirSync(dir).forEach((file) => {
            const dirFile = path.join(dir, file);
            if (fs.statSync(dirFile).isDirectory()) {
                filelist = walkSync(dirFile, filelist);
            }
            else {
                const relPath = path.relative((0, constants_1.getRootDir)(), dirFile);
                if (!ignoreSpec.match_file(relPath)) {
                    filelist.push(relPath);
                }
            }
        });
        return filelist;
    };
    return walkSync((0, constants_1.getRootDir)());
}
class CodeContext {
    constructor() {
        this.knownFiles = [];
    }
    copySrc() {
        const destDir = (0, constants_1.getArtifactsDir)();
        if (!fs.existsSync(destDir)) {
            fs.mkdirSync(destDir, { recursive: true });
        }
        const filesToCopy = getAllSrcFiles();
        for (const relPath of filesToCopy) {
            const srcPath = path.join((0, constants_1.getRootDir)(), relPath);
            const destPath = path.join(destDir, relPath);
            fs.mkdirSync(path.dirname(destPath), { recursive: true });
            shutil.copySync(srcPath, destPath);
        }
        this.knownFiles = filesToCopy;
        return this.knownFiles;
    }
}
exports.CodeContext = CodeContext;
if (require.main === module) {
    for (const file of getAllSrcFiles()) {
        console.log(file);
    }
}
