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
exports.ASTParser = void 0;
const ts = __importStar(require("typescript"));
const fs = __importStar(require("fs"));
class ASTParser {
    constructor() {
        this.cache = new Map();
    }
    parseFile(filePath) {
        if (!this.cache.has(filePath)) {
            const fileContents = fs.readFileSync(filePath, 'utf8');
            const sourceFile = ts.createSourceFile(filePath, fileContents, ts.ScriptTarget.Latest, true);
            this.cache.set(filePath, sourceFile);
        }
        return this.cache.get(filePath);
    }
    getFullyQualifiedName(node) {
        if (ts.isIdentifier(node)) {
            return node.text;
        }
        else if (ts.isPropertyAccessExpression(node)) {
            return `${this.getFullyQualifiedName(node.expression)}.${node.name.text}`;
        }
        else if (ts.isClassDeclaration(node) || ts.isFunctionDeclaration(node)) {
            return node.name ? node.name.text : '';
        }
        return '';
    }
    getImports(filePath) {
        const imports = [];
        const sourceFile = this.parseFile(filePath);
        sourceFile.forEachChild(node => {
            if (ts.isImportDeclaration(node)) {
                const moduleName = node.moduleSpecifier.getText(sourceFile);
                imports.push(moduleName.slice(1, -1)); // Remove the quotes
            }
        });
        return imports;
    }
    getExports(filePath) {
        const exports = [];
        const sourceFile = this.parseFile(filePath);
        sourceFile.forEachChild(node => {
            var _a;
            if (ts.isFunctionDeclaration(node) || ts.isClassDeclaration(node)) {
                if ((_a = node.modifiers) === null || _a === void 0 ? void 0 : _a.some(modifier => modifier.kind === ts.SyntaxKind.ExportKeyword)) {
                    exports.push(this.getFullyQualifiedName(node));
                }
            }
        });
        return exports;
    }
    summarizeModules(files) {
        const summaries = {};
        files.forEach(filePath => {
            const summary = {
                functions: [],
                classes: [],
                imports: this.getImports(filePath),
                exports: this.getExports(filePath),
            };
            const sourceFile = this.parseFile(filePath);
            sourceFile.forEachChild(node => {
                if (ts.isFunctionDeclaration(node) && node.name) {
                    summary.functions.push(node.name.text);
                }
                else if (ts.isClassDeclaration(node) && node.name) {
                    summary.classes.push(node.name.text);
                }
            });
            summaries[filePath] = summary;
        });
        return summaries;
    }
}
exports.ASTParser = ASTParser;
// Example usage
if (require.main === module) {
    const parser = new ASTParser();
    const filesToAnalyze = ['path/to/file1.ts', 'path/to/file2.ts'];
    const summaries = parser.summarizeModules(filesToAnalyze);
    console.log(summaries);
}
