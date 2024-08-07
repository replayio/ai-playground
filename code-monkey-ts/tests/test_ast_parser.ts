import * as fs from "fs";
import * as path from "path";
import { ASTParser } from "../deps/ast_parser";

describe("ASTParser", () => {
  let parser: ASTParser;

  beforeEach(() => {
    parser = new ASTParser();
  });

  afterEach(() => {});

  describe("parseFile", () => {
    it("should parse a TypeScript file", () => {
      const filePath = path.join(__dirname, "samples", "sample_a.ts");
      const sourceFile = parser.parseFile(filePath);
      expect(sourceFile).not.toBeNull();
      expect(sourceFile.fileName).toEqual(filePath);
    });
  });

  describe("getFullyQualifiedName", () => {
    it("should return the fully qualified name for a class", () => {
      const filePath = path.join(__dirname, "samples", "sample_a.ts");
      const sourceFile = parser.parseFile(filePath);
      const classNode = sourceFile.statements.find((node) => node.kind === 229); // ClassDeclaration
      if (classNode) {
        const fullyQualifiedName = parser.getFullyQualifiedName(classNode);
        expect(fullyQualifiedName).toEqual("SampleClass");
      } else {
        throw new Error("ClassDeclaration not found in the file");
      }
    });
  });

  describe("getImports", () => {
    it("should return a list of imports", () => {
      const filePath = path.join(__dirname, "samples", "sample_b.ts");
      const imports = parser.getImports(filePath);
      expect(imports).toEqual(["path", "fs", "./sample_a"]);
    });
  });

  describe("getExports", () => {
    it("should return a list of exports", () => {
      const filePath = path.join(__dirname, "samples", "sample_b.ts");
      const exports = parser.getExports(filePath);
      expect(exports).toEqual(["SampleFunction", "SampleClass"]);
    });
  });

  describe("summarizeModules", () => {
    it("should summarize multiple modules", () => {
      const files = [
        path.join(__dirname, "samples", "sample_a.ts"),
        path.join(__dirname, "samples", "sample_b.ts"),
      ];
      const summaries = parser.summarizeModules(files);
      expect(Object.keys(summaries)).toHaveLength(2);
      expect(summaries[files[0]].classes).toEqual(["SampleClass"]);
      expect(summaries[files[1]].functions).toEqual(["SampleFunction"]);
    });
  });
});

// Main execution
if (require.main === module) {
  describe("ASTParser", () => {
    it("should run all tests", () => {
      // This will run all the tests defined above
    });
  });
}
