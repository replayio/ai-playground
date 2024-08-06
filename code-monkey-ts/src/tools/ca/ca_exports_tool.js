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
exports.addExport = addExport;
exports.runCAExports = runCAExports;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const util_1 = require("util");
const child_process_1 = require("child_process");
const readFile = (0, util_1.promisify)(fs.readFile);
const writeFile = (0, util_1.promisify)(fs.writeFile);
const execAsync = (0, util_1.promisify)(child_process_1.exec);
function addExport(filePath, exportStatement) {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            const absolutePath = path.resolve(filePath);
            let fileContent = yield readFile(absolutePath, 'utf8');
            // Check if the export already exists
            if (fileContent.includes(exportStatement)) {
                return {
                    success: false,
                    message: 'Export already exists in the file.',
                };
            }
            // Add the export statement at the end of the file
            fileContent += '\n' + exportStatement + '\n';
            yield writeFile(absolutePath, fileContent, 'utf8');
            return {
                success: true,
                message: 'Export added successfully.',
            };
        }
        catch (error) {
            return {
                success: false,
                message: `Error: ${error.message}`,
            };
        }
    });
}
function runCAExports(filePath) {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            const absolutePath = path.resolve(filePath);
            const command = `ca exports "${absolutePath}"`;
            const { stdout, stderr } = yield execAsync(command);
            if (stderr) {
                return {
                    success: false,
                    message: `Error: ${stderr}`,
                };
            }
            return {
                success: true,
                message: 'CA exports command executed successfully.',
                output: stdout.trim(),
            };
        }
        catch (error) {
            return {
                success: false,
                message: `Error: ${error.message}`,
            };
        }
    });
}
// Main execution
if (require.main === module) {
    (() => __awaiter(void 0, void 0, void 0, function* () {
        if (process.argv.length < 3 || process.argv.length > 4) {
            console.error('Usage: node ca_exports_tool.js <file_path> [export_statement]');
            process.exit(1);
        }
        const [, , filePath, exportStatement] = process.argv;
        if (exportStatement) {
            const result = yield addExport(filePath, exportStatement);
            console.log(result.message);
        }
        else {
            const result = yield runCAExports(filePath);
            console.log(result.message);
            if (result.output) {
                console.log('Output:', result.output);
            }
        }
        process.exit(result.success ? 0 : 1);
    }))();
}
