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
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.CodeContext = void 0;
exports.getAllSrcFiles = getAllSrcFiles;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const util = __importStar(require("util"));
const constants_1 = require("./constants");
const readFile = util.promisify(fs.readFile);
const writeFile = util.promisify(fs.writeFile);
const mkdir = util.promisify(fs.mkdir);
const copyFile = util.promisify(fs.copyFile);
// Simple implementation of gitignore-style pattern matching
function matchesGitIgnorePattern(filePath, pattern) {
    const regexPattern = pattern
        .replace(/\./g, '\\.')
        .replace(/\*/g, '.*')
        .replace(/\?/g, '.');
    const regex = new RegExp(`^${regexPattern}$`);
    return regex.test(filePath);
}
function getAllSrcFiles() {
    return __awaiter(this, void 0, void 0, function* () {
        const srcFiles = [];
        const rootDir = (0, constants_1.getRootDir)();
        // Read .gitignore patterns
        let gitignorePatterns = ['.git'];
        // Check current directory and up to max 3 parent directories until we hit our root dir
        for (let i = 0; i < 4; i++) {
            const dirPath = path.resolve(__dirname, ...Array(i).fill('..'));
            const gitignorePath = path.join(dirPath, '.gitignore');
            console.debug(`checking gitignore path ${gitignorePath}`);
            if (fs.existsSync(gitignorePath)) {
                console.debug('   found it');
                const gitignoreContent = yield readFile(gitignorePath, 'utf-8');
                gitignorePatterns = gitignorePatterns.concat(gitignoreContent.split('\n'));
            }
            if (dirPath === rootDir) {
                break;
            }
        }
        // Walk through the directory
        const walk = (dir) => {
            const files = fs.readdirSync(dir);
            for (const file of files) {
                const filePath = path.join(dir, file);
                const stat = fs.statSync(filePath);
                if (stat.isDirectory()) {
                    walk(filePath);
                }
                else {
                    const relPath = path.relative(rootDir, filePath);
                    if (!gitignorePatterns.some(pattern => matchesGitIgnorePattern(relPath, pattern))) {
                        srcFiles.push(relPath);
                    }
                }
            }
        };
        walk(rootDir);
        return srcFiles;
    });
}
class CodeContext {
    constructor() {
        this.knownFiles = [];
    }
    copySrc() {
        return __awaiter(this, void 0, void 0, function* () {
            const destDir = (0, constants_1.getArtifactsDir)();
            if (!fs.existsSync(destDir)) {
                yield mkdir(destDir, { recursive: true });
            }
            const filesToCopy = yield getAllSrcFiles();
            for (const relPath of filesToCopy) {
                const srcPath = path.join((0, constants_1.getRootDir)(), relPath);
                const destPath = path.join(destDir, relPath);
                yield mkdir(path.dirname(destPath), { recursive: true });
                yield copyFile(srcPath, destPath);
            }
            this.knownFiles = filesToCopy;
            return this.knownFiles;
        });
    }
}
exports.CodeContext = CodeContext;
// Main execution
if (require.main === module) {
    (() => __awaiter(void 0, void 0, void 0, function* () {
        const files = yield getAllSrcFiles();
        for (const file of files) {
            console.log(file);
        }
    }))();
}
