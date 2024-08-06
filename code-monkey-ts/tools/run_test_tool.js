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
var __runInitializers = (this && this.__runInitializers) || function (thisArg, initializers, value) {
    var useValue = arguments.length > 2;
    for (var i = 0; i < initializers.length; i++) {
        value = useValue ? initializers[i].call(thisArg, value) : initializers[i].call(thisArg);
    }
    return useValue ? value : void 0;
};
var __esDecorate = (this && this.__esDecorate) || function (ctor, descriptorIn, decorators, contextIn, initializers, extraInitializers) {
    function accept(f) { if (f !== void 0 && typeof f !== "function") throw new TypeError("Function expected"); return f; }
    var kind = contextIn.kind, key = kind === "getter" ? "get" : kind === "setter" ? "set" : "value";
    var target = !descriptorIn && ctor ? contextIn["static"] ? ctor : ctor.prototype : null;
    var descriptor = descriptorIn || (target ? Object.getOwnPropertyDescriptor(target, contextIn.name) : {});
    var _, done = false;
    for (var i = decorators.length - 1; i >= 0; i--) {
        var context = {};
        for (var p in contextIn) context[p] = p === "access" ? {} : contextIn[p];
        for (var p in contextIn.access) context.access[p] = contextIn.access[p];
        context.addInitializer = function (f) { if (done) throw new TypeError("Cannot add initializers after decoration has completed"); extraInitializers.push(accept(f || null)); };
        var result = (0, decorators[i])(kind === "accessor" ? { get: descriptor.get, set: descriptor.set } : descriptor[key], context);
        if (kind === "accessor") {
            if (result === void 0) continue;
            if (result === null || typeof result !== "object") throw new TypeError("Object expected");
            if (_ = accept(result.get)) descriptor.get = _;
            if (_ = accept(result.set)) descriptor.set = _;
            if (_ = accept(result.init)) initializers.unshift(_);
        }
        else if (_ = accept(result)) {
            if (kind === "field") initializers.unshift(_);
            else descriptor[key] = _;
        }
    }
    if (target) Object.defineProperty(target, contextIn.name, descriptor);
    done = true;
};
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
exports.instrumentedRunTestTool = exports.runTestTool = void 0;
const fs = __importStar(require("fs/promises"));
const path = __importStar(require("path"));
const os = __importStar(require("os"));
const child_process_1 = require("child_process");
const zod_1 = require("zod");
const tools_1 = require("@langchain/core/tools");
const instrumentation_1 = require("../instrumentation");
const RunTestToolInputSchema = zod_1.z.object({
    test_file: zod_1.z.string().describe("The path to the test file to run"),
    profile: zod_1.z.boolean().optional().describe("Whether to run the test with profiling")
});
let RunTestTool = (() => {
    var _a;
    let _classSuper = tools_1.Tool;
    let _instanceExtraInitializers = [];
    let __call_decorators;
    return _a = class RunTestTool extends _classSuper {
            constructor(fields) {
                super(fields);
                this.name = (__runInitializers(this, _instanceExtraInitializers), "run_test");
                this.description = "Run a TypeScript test file and return the results";
                this.schema = RunTestToolInputSchema;
            }
            cleanup(tempFiles) {
                return __awaiter(this, void 0, void 0, function* () {
                    for (const file of tempFiles) {
                        try {
                            yield fs.unlink(file);
                        }
                        catch (error) {
                            console.error(`Error deleting temporary file ${file}:`, error);
                        }
                    }
                });
            }
            runTestWithProfiling(testFile) {
                return __awaiter(this, void 0, void 0, function* () {
                    const tempProfileFile = path.join(os.tmpdir(), `profile_${Date.now()}.txt`);
                    const command = `ts-node --prof ${testFile} > ${tempProfileFile}`;
                    try {
                        const result = yield this.runCommand(command);
                        const profileOutput = yield this.summarizeProfilingOutput(tempProfileFile);
                        return Object.assign(Object.assign({}, result), { output: `${result.output}\n\nProfiling Summary:\n${profileOutput}` });
                    }
                    finally {
                        yield this.cleanup([tempProfileFile]);
                    }
                });
            }
            summarizeProfilingOutput(profileFile) {
                return __awaiter(this, void 0, void 0, function* () {
                    const command = `node --prof-process ${profileFile}`;
                    const result = yield this.runCommand(command);
                    return result.output;
                });
            }
            runCommand(command) {
                return new Promise((resolve) => {
                    const process = (0, child_process_1.spawn)(command, { shell: true });
                    let output = '';
                    let error = '';
                    process.stdout.on('data', (data) => {
                        output += data.toString();
                    });
                    process.stderr.on('data', (data) => {
                        error += data.toString();
                    });
                    process.on('close', (code) => {
                        resolve({
                            output,
                            error: error || null,
                            returncode: code !== null && code !== void 0 ? code : 0
                        });
                    });
                });
            }
            _call(_b, runManager_1) {
                return __awaiter(this, arguments, void 0, function* ({ test_file, profile = false }, runManager) {
                    try {
                        const result = profile
                            ? yield this.runTestWithProfiling(test_file)
                            : yield this.runCommand(`ts-node ${test_file}`);
                        return JSON.stringify({
                            output: result.output,
                            error: result.error,
                            returncode: result.returncode
                        });
                    }
                    catch (error) {
                        console.error("Error running test:", error);
                        throw error;
                    }
                });
            }
        },
        (() => {
            var _b;
            const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create((_b = _classSuper[Symbol.metadata]) !== null && _b !== void 0 ? _b : null) : void 0;
            __call_decorators = [(0, instrumentation_1.instrument)("Tool.call", ["test_file", "profile"], { attributes: { tool: "RunTestTool" } })];
            __esDecorate(_a, null, __call_decorators, { kind: "method", name: "_call", static: false, private: false, access: { has: obj => "_call" in obj, get: obj => obj._call }, metadata: _metadata }, null, _instanceExtraInitializers);
            if (_metadata) Object.defineProperty(_a, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
        })(),
        _a;
})();
exports.runTestTool = new RunTestTool();
// Wrapper function to apply the instrumentation decorator
exports.instrumentedRunTestTool = (0, instrumentation_1.instrument)("Tool.call", ["test_file", "profile"], { attributes: { tool: "RunTestTool" } })(exports.runTestTool._call.bind(exports.runTestTool));
// You can use the instrumented version like this:
// runTestTool._call = instrumentedRunTestTool;
