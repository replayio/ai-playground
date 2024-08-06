"use strict";
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
exports.instrumentedReadFileTool = exports.readFileTool = void 0;
const fs_1 = require("fs");
const zod_1 = require("zod");
const tools_1 = require("@langchain/core/tools");
const utils_1 = require("./utils");
const instrumentation_1 = require("../instrumentation");
const ReadFileToolInputSchema = zod_1.z.object({
    fname: zod_1.z.string().describe("The name of the file to read")
});
exports.readFileTool = (0, tools_1.tool)({
    name: "read_file",
    description: "Read the contents of the file of given name",
    schema: ReadFileToolInputSchema,
    func: (_a, runManager_1) => __awaiter(void 0, [_a, runManager_1], void 0, function* ({ fname }, runManager) {
        const filePath = (0, utils_1.makeFilePath)(fname);
        try {
            const content = yield fs_1.promises.readFile(filePath, 'utf-8');
            return content;
        }
        catch (error) {
            console.error(`Failed to open file for reading: ${filePath}`);
            console.error(error);
            // Re-throw the error
            throw error;
        }
    })
});
// Wrapper function to apply the instrumentation decorator
exports.instrumentedReadFileTool = (0, instrumentation_1.instrument)("Tool.func", ["fname"], { attributes: { tool: "ReadFileTool" } })(exports.readFileTool.func);
// You can use the instrumented version like this:
// readFileTool.func = instrumentedReadFileTool;
