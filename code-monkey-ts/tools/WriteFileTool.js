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
exports.instrumentedWriteFileTool = exports.writeFileTool = void 0;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const zod_1 = require("zod");
const tools_1 = require("@langchain/core/tools");
const utils_1 = require("../utils");
const instrumentation_1 = require("../../instrumentation");
const WriteFileToolInputSchema = zod_1.z.object({
    fname: zod_1.z.string().describe("Name of the file to edit."),
    content: zod_1.z.string().describe("New contents of the file.")
});
exports.writeFileTool = (0, tools_1.tool)({
    name: "write_file",
    description: "Write content to the file of given name",
    schema: WriteFileToolInputSchema,
    func: (_a, runManager_1) => __awaiter(void 0, [_a, runManager_1], void 0, function* ({ fname, content }, runManager) {
        const filePath = (0, utils_1.makeFilePath)(fname);
        try {
            yield fs.promises.mkdir(path.dirname(filePath), { recursive: true });
            yield fs.promises.writeFile(filePath, content);
            notifyFileModified(fname);
            return `File ${fname} has been written successfully.`;
        }
        catch (error) {
            console.error(`Failed to write file: ${filePath}`);
            console.error(error);
            throw error;
        }
    })
});
function notifyFileModified(fname) {
    // Implement file modification notification logic here
    console.log(`File modified: ${fname}`);
}
// Wrapper function to apply the instrumentation decorator
exports.instrumentedWriteFileTool = (0, instrumentation_1.instrument)("Tool.func", ["fname", "content"], { attributes: { tool: "WriteFileTool" } })(exports.writeFileTool.func);
// You can use the instrumented version like this:
// writeFileTool.func = instrumentedWriteFileTool;
// Simple test case
if (require.main === module) {
    (() => __awaiter(void 0, void 0, void 0, function* () {
        const testFileName = 'test_write_file.txt';
        const testContent = 'This is a test content.';
        try {
            const result = yield exports.writeFileTool.func({ fname: testFileName, content: testContent });
            console.log(result);
            const fileContent = yield fs.promises.readFile((0, utils_1.makeFilePath)(testFileName), 'utf-8');
            if (fileContent === testContent) {
                console.log('Test passed: File content matches the input.');
            }
            else {
                console.error('Test failed: File content does not match the input.');
            }
            yield fs.promises.unlink((0, utils_1.makeFilePath)(testFileName));
        }
        catch (error) {
            console.error('Test failed:', error);
        }
    }))();
}
