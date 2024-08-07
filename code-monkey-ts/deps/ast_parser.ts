import * as ts from 'typescript';
import * as fs from 'fs';
import * as path from 'path';

interface ModuleSummary {
  functions: string[];
  classes: string[];
  imports: string[];
  exports: string[];
}

class ASTParser {
  private cache: Map<string, ts.SourceFile> = new Map();

  parseFile(filePath: string): ts.SourceFile {
    if (!this.cache.has(filePath)) {
      const fileContents = fs.readFileSync(filePath, 'utf8');
      const sourceFile = ts.createSourceFile(
        filePath,
        fileContents,
        ts.ScriptTarget.Latest,
        true
      );
      this.cache.set(filePath, sourceFile);
    }
    return this.cache.get(filePath)!;
  }

  getFullyQualifiedName(node: ts.Node): string {
    if (ts.isIdentifier(node)) {
      return node.text;
    } else if (ts.isPropertyAccessExpression(node)) {
      return `${this.getFullyQualifiedName(node.expression)}.${node.name.text}`;
    } else if (ts.isClassDeclaration(node) || ts.isFunctionDeclaration(node)) {
      return node.name ? node.name.text : '';
    }
    return '';
  }

  getImports(filePath: string): string[] {
    const imports: string[] = [];
    const sourceFile = this.parseFile(filePath);
    sourceFile.forEachChild(node => {
      if (ts.isImportDeclaration(node)) {
        const moduleName = node.moduleSpecifier.getText(sourceFile);
        imports.push(moduleName.slice(1, -1)); // Remove the quotes
      }
    });
    return imports;
  }

  getExports(filePath: string): string[] {
    const exports: string[] = [];
    const sourceFile = this.parseFile(filePath);
    sourceFile.forEachChild(node => {
      if (ts.isFunctionDeclaration(node) || ts.isClassDeclaration(node)) {
        if (node.modifiers?.some(modifier => modifier.kind === ts.SyntaxKind.ExportKeyword)) {
          exports.push(this.getFullyQualifiedName(node));
        }
      }
    });
    return exports;
  }

  summarizeModules(files: string[]): Record<string, ModuleSummary> {
    const summaries: Record<string, ModuleSummary> = {};
    files.forEach(filePath => {
      const summary: ModuleSummary = {
        functions: [],
        classes: [],
        imports: this.getImports(filePath),
        exports: this.getExports(filePath),
      };
      const sourceFile = this.parseFile(filePath);
      sourceFile.forEachChild(node => {
        if (ts.isFunctionDeclaration(node) && node.name) {
          summary.functions.push(node.name.text);
        } else if (ts.isClassDeclaration(node) && node.name) {
          summary.classes.push(node.name.text);
        }
      });
      summaries[filePath] = summary;
    });
    return summaries;
  }
}

// Example usage
if (require.main === module) {
  const parser = new ASTParser();
  const filesToAnalyze = ['path/to/file1.ts', 'path/to/file2.ts'];
  const summaries = parser.summarizeModules(filesToAnalyze);
  console.log(summaries);
}

export { ASTParser, ModuleSummary };
