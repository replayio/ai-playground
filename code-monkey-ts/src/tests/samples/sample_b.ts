import { expect } from 'chai';
import * as sinon from 'sinon';
import * as fs from 'fs';
import * as path from 'path';
import { ASTParser } from '../../deps/ast_parser';

describe('ASTParser', () => {
    let sandbox: sinon.SinonSandbox;
    let parser: ASTParser;

    beforeEach(() => {
        sandbox = sinon.createSandbox();
        parser = new ASTParser();
    });

    afterEach(() => {
        sandbox.restore();
    });

    describe('parseFile', () => {
        it('should parse a TypeScript file', () => {
            const filePath = path.join(__dirname, 'sample_b.ts');
            const sourceFile = parser.parseFile(filePath);
            expect(sourceFile).to.not.be.null;
            expect(sourceFile.fileName).to.equal(filePath);
        });
    });

    describe('getFullyQualifiedName', () => {
        it('should return the fully qualified name for a class', () => {
            const filePath = path.join(__dirname, 'sample_b.ts');
            const sourceFile = parser.parseFile(filePath);
            const classNode = sourceFile.statements.find(node => node.kind === 229); // ClassDeclaration
            const fullyQualifiedName = parser.getFullyQualifiedName(classNode);
            expect(fullyQualifiedName).to.equal('SampleClass');
        });
    });

    describe('getImports', () => {
        it('should return a list of imports', () => {
            const filePath = path.join(__dirname, 'sample_b.ts');
            const imports = parser.getImports(filePath);
            expect(imports).to.deep.equal(['path', 'fs']);
        });
    });

    describe('getExports', () => {
        it('should return a list of exports', () => {
            const filePath = path.join(__dirname, 'sample_b.ts');
            const exports = parser.getExports(filePath);
            expect(exports).to.deep.equal(['SampleFunction', 'SampleClass']);
        });
    });

    describe('summarizeModules', () => {
        it('should summarize multiple modules', () => {
            const files = [
                path.join(__dirname, 'sample_a.ts'),
                path.join(__dirname, 'sample_b.ts')
            ];
            const summaries = parser.summarizeModules(files);
            expect(Object.keys(summaries)).to.have.lengthOf(2);
            expect(summaries[files[0]].classes).to.deep.equal(['SampleClass']);
            expect(summaries[files[1]].functions).to.deep.equal(['SampleFunction']);
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
