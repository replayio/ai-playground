"use strict";
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
exports.rgTool = void 0;
const child_process_1 = require("child_process");
const zod_1 = require("zod");
const tools_1 = require("@langchain/core/tools");
const constants_1 = require("../constants");
const instrumentation_1 = require("../instrumentation");
const RgToolInputSchema = zod_1.z.object({
    pattern: zod_1.z.string().describe("The pattern to search for.")
});
let RgTool = (() => {
    var _a;
    let _instanceExtraInitializers = [];
    let __run_decorators;
    return _a = class RgTool {
            constructor() {
                this.name = (__runInitializers(this, _instanceExtraInitializers), "rg");
                this.description = "Search for a pattern in files within the artifacts folder using ripgrep";
            }
            _run(_b, runManager_1) {
                return __awaiter(this, arguments, void 0, function* ({ pattern }, runManager) {
                    console.debug(`get_artifacts_dir(): ${(0, constants_1.getArtifactsDir)()}`);
                    return this._searchWithRg(pattern);
                });
            }
            _searchWithRg(pattern) {
                return __awaiter(this, void 0, void 0, function* () {
                    const command = ["rg", "-i", "--no-heading", "--with-filename", "-r", pattern, "."];
                    console.debug(`Current working directory: ${process.cwd()}`);
                    console.debug(`Executing command: ${command.join(' ')}`);
                    return new Promise((resolve, reject) => {
                        const rg = (0, child_process_1.spawn)('rg', command.slice(1), { cwd: (0, constants_1.getArtifactsDir)() });
                        let stdout = '';
                        let stderr = '';
                        rg.stdout.on('data', (data) => {
                            stdout += data.toString();
                        });
                        rg.stderr.on('data', (data) => {
                            stderr += data.toString();
                        });
                        rg.on('close', (code) => {
                            console.debug(`Raw output: ${stdout}`);
                            if (code === 0) {
                                resolve(stdout.trim() || "0 matches found.");
                            }
                            else if (code === 1) {
                                console.debug("No matches found");
                                resolve("0 matches found.");
                            }
                            else {
                                console.error(`Error occurred: ${stderr}`);
                                reject(new Error(`Error occurred: ${stderr}`));
                            }
                        });
                    });
                });
            }
        },
        (() => {
            const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create(null) : void 0;
            __run_decorators = [(0, instrumentation_1.instrument)("Tool._run", ["pattern"], { attributes: { tool: "RgTool" } })];
            __esDecorate(_a, null, __run_decorators, { kind: "method", name: "_run", static: false, private: false, access: { has: obj => "_run" in obj, get: obj => obj._run }, metadata: _metadata }, null, _instanceExtraInitializers);
            if (_metadata) Object.defineProperty(_a, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
        })(),
        _a;
})();
exports.rgTool = (0, tools_1.tool)({
    name: "rg",
    description: "Search for a pattern in files within the artifacts folder using ripgrep",
    schema: RgToolInputSchema,
    func: (input, runManager) => __awaiter(void 0, void 0, void 0, function* () {
        const tool = new RgTool();
        return tool._run(input, runManager);
    })
});
