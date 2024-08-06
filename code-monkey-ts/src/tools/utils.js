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
exports.getFileExtension = getFileExtension;
exports.getFilenameWithoutExtension = getFilenameWithoutExtension;
exports.readFileContent = readFileContent;
exports.writeFileContent = writeFileContent;
exports.joinPaths = joinPaths;
exports.getAbsolutePath = getAbsolutePath;
exports.getRelativePath = getRelativePath;
exports.fileExists = fileExists;
exports.isDirectory = isDirectory;
exports.createDirectory = createDirectory;
exports.listFiles = listFiles;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const util_1 = require("util");
const readFile = (0, util_1.promisify)(fs.readFile);
const writeFile = (0, util_1.promisify)(fs.writeFile);
function getFileExtension(filename) {
    return path.extname(filename).slice(1);
}
function getFilenameWithoutExtension(filename) {
    return path.basename(filename, path.extname(filename));
}
function readFileContent(filePath) {
    return __awaiter(this, void 0, void 0, function* () {
        return yield readFile(filePath, 'utf-8');
    });
}
function writeFileContent(filePath, content) {
    return __awaiter(this, void 0, void 0, function* () {
        yield writeFile(filePath, content, 'utf-8');
    });
}
function joinPaths(...paths) {
    return path.join(...paths);
}
function getAbsolutePath(relativePath) {
    return path.resolve(relativePath);
}
function getRelativePath(from, to) {
    return path.relative(from, to);
}
function fileExists(filePath) {
    return fs.existsSync(filePath);
}
function isDirectory(path) {
    return fs.statSync(path).isDirectory();
}
function createDirectory(dirPath) {
    fs.mkdirSync(dirPath, { recursive: true });
}
function listFiles(dirPath) {
    return fs.readdirSync(dirPath);
}
// Main execution
if (require.main === module) {
    console.log('This module provides utility functions for file and path operations.');
    console.log('Import and use these functions in your TypeScript code as needed.');
}
