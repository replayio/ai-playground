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
exports.instrumentedRenameFileTool = exports.renameFileTool = void 0;
const fs_1 = require("fs");
const path = __importStar(require("path"));
const zod_1 = require("zod");
const tools_1 = require("@langchain/core/tools");
const utils_1 = require("../utils");
const instrumentation_1 = require("../../instrumentation");
const RenameFileToolInputSchema = zod_1.z.object({
    oldName: zod_1.z.string().describe("Current name of the file."),
    newName: zod_1.z.string().describe("New name for the file.")
});
exports.renameFileTool = new tools_1.StructuredTool({
    name: "rename_file",
    description: "Rename a file, given old and new names",
    schema: RenameFileToolInputSchema,
    func: (_a, runManager_1) => __awaiter(void 0, [_a, runManager_1], void 0, function* ({ oldName, newName }, runManager) {
        const oldPath = (0, utils_1.makeFilePath)(oldName);
        const newPath = (0, utils_1.makeFilePath)(newName);
        try {
            yield fs_1.promises.access(oldPath);
        }
        catch (_b) {
            throw new Error(`The file ${oldName} does not exist.`);
        }
        const newDir = path.dirname(newPath);
        yield fs_1.promises.mkdir(newDir, { recursive: true });
        try {
            yield fs_1.promises.access(newPath);
            throw new Error(`The file ${newName} already exists.`);
        }
        catch (_c) {
            // File does not exist, which is expected
        }
        yield fs_1.promises.rename(oldPath, newPath);
        return `File renamed from ${oldName} to ${newName}`;
    })
});
// Wrapper function to apply the instrumentation decorator
exports.instrumentedRenameFileTool = (0, instrumentation_1.instrument)("Tool.func", ["oldName", "newName"], { attributes: { tool: "RenameFileTool" } })(exports.renameFileTool.func);
// You can use the instrumented version like this:
// renameFileTool.func = instrumentedRenameFileTool;
