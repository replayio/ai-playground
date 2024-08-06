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
exports.runRipgrep = runRipgrep;
const child_process_1 = require("child_process");
const util_1 = require("util");
const execAsync = (0, util_1.promisify)(child_process_1.exec);
function runRipgrep(pattern_1, path_1) {
    return __awaiter(this, arguments, void 0, function* (pattern, path, flags = []) {
        const command = `rg ${flags.join(' ')} "${pattern}" "${path}"`;
        try {
            const { stdout, stderr } = yield execAsync(command);
            return {
                success: true,
                output: stdout.trim(),
            };
        }
        catch (error) {
            if (error.code === 1 && !error.stderr) {
                // No matches found, but command executed successfully
                return {
                    success: true,
                    output: '',
                };
            }
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
        if (process.argv.length < 4) {
            console.error('Usage: node rg_tool.js <pattern> <path> [flags...]');
            process.exit(1);
        }
        const [, , pattern, path, ...flags] = process.argv;
        const result = yield runRipgrep(pattern, path, flags);
        if (result.success) {
            console.log(result.output);
        }
        else {
            console.error(result.error);
        }
        process.exit(result.success ? 0 : 1);
    }))();
}
