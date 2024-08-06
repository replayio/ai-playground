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
exports.runTestTool = runTestTool;
const child_process_1 = require("child_process");
const util_1 = require("util");
const execAsync = (0, util_1.promisify)(child_process_1.exec);
function runTestTool(testCommand) {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            const { stdout, stderr } = yield execAsync(testCommand);
            return {
                success: true,
                output: stdout.trim(),
                error: stderr.trim(),
            };
        }
        catch (error) {
            return {
                success: false,
                error: error.message,
            };
        }
    });
}
// Main execution
if (require.main === module) {
    (() => __awaiter(void 0, void 0, void 0, function* () {
        if (process.argv.length < 3) {
            console.error('Usage: node run_test_tool.js <test_command>');
            process.exit(1);
        }
        const testCommand = process.argv.slice(2).join(' ');
        const result = yield runTestTool(testCommand);
        if (result.success) {
            console.log('Test output:');
            console.log(result.output);
            if (result.error) {
                console.error('Test errors:');
                console.error(result.error);
            }
        }
        else {
            console.error('Test execution failed:');
            console.error(result.error);
        }
        process.exit(result.success ? 0 : 1);
    }))();
}
