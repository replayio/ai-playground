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
const chai_1 = require("chai");
const sinon = __importStar(require("sinon"));
const path = __importStar(require("path"));
const ast_parser_1 = require("../deps/ast_parser");
describe('ASTParser', () => {
    let sandbox;
    let parser;
    beforeEach(() => {
        sandbox = sinon.createSandbox();
        parser = new ast_parser_1.ASTParser();
    });
    afterEach(() => {
        sandbox.restore();
    });
    describe('parseFile', () => {
        it('should parse a TypeScript file', () => {
            const filePath = path.join(__dirname, 'samples', 'sample_a.ts');
            const sourceFile = parser.parseFile(filePath);
            (0, chai_1.expect)(sourceFile).to.not.be.null;
            (0, chai_1.expect)(sourceFile.fileName).to.equal(filePath);
        });
    });
    describe('getFullyQualifiedName', () => {
        it('should return the fully qualified name for a class', () => {
            const filePath = path.join(__dirname, 'samples', 'sample_a.ts');
            const sourceFile = parser.parseFile(filePath);
            const classNode = sourceFile.statements.find(node => node.kind === 229); // ClassDeclaration
            const fullyQualifiedName = parser.getFullyQualifiedName(classNode);
            (0, chai_1.expect)(fullyQualifiedName).to.equal('SampleClass');
        });
    });
    describe('getImports', () => {
        it('should return a list of imports', () => {
            const filePath = path.join(__dirname, 'samples', 'sample_b.ts');
            const imports = parser.getImports(filePath);
            (0, chai_1.expect)(imports).to.deep.equal(['path', 'fs', './sample_a']);
        });
    });
    describe('getExports', () => {
        it('should return a list of exports', () => {
            const filePath = path.join(__dirname, 'samples', 'sample_b.ts');
            const exports = parser.getExports(filePath);
            (0, chai_1.expect)(exports).to.deep.equal(['SampleFunction', 'SampleClass']);
        });
    });
    describe('summarizeModules', () => {
        it('should summarize multiple modules', () => {
            const files = [
                path.join(__dirname, 'samples', 'sample_a.ts'),
                path.join(__dirname, 'samples', 'sample_b.ts')
            ];
            const summaries = parser.summarizeModules(files);
            (0, chai_1.expect)(Object.keys(summaries)).to.have.lengthOf(2);
            (0, chai_1.expect)(summaries[files[0]].classes).to.deep.equal(['SampleClass']);
            (0, chai_1.expect)(summaries[files[1]].functions).to.deep.equal(['SampleFunction']);
        });
    });
});
// Main execution
if (require.main === module) {
    describe('ASTParser', () => {
        it('should run all tests', () => {
            // This will run all the tests defined above
        });
    });
}
