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
exports.caASTAnalyzerTool = exports.CAASTAnalyzerTool = void 0;
const zod_1 = require("zod");
const tools_1 = require("@langchain/core/tools");
const CATool_1 = require("./CATool");
const deps_1 = require("../deps");
const instrumentation_1 = require("../../instrumentation");
const CAASTAnalyzerToolInputSchema = zod_1.z.object({
    files: zod_1.z.array(zod_1.z.string()).optional().describe("List of relative file paths to analyze"),
    modules: zod_1.z.array(zod_1.z.string()).optional().describe("List of modules to analyze")
}).refine(data => data.files != null || data.modules != null, {
    message: "Either 'files' or 'modules' must be provided"
});
let CAASTAnalyzerTool = (() => {
    var _a;
    let _classSuper = CATool_1.CATool;
    let _instanceExtraInitializers = [];
    let __run_decorators;
    return _a = class CAASTAnalyzerTool extends _classSuper {
            constructor() {
                super();
                this.name = (__runInitializers(this, _instanceExtraInitializers), "ca_analyze_ast");
                this.description = "Analyze the Abstract Syntax Tree of Python files";
                this.argsSchema = CAASTAnalyzerToolInputSchema;
            }
            _run(input, runManager) {
                return __awaiter(this, void 0, void 0, function* () {
                    const { files = [], modules = [] } = input;
                    const allFiles = [
                        ...files.map(deps_1.resolveFilePath),
                        ...modules.map(deps_1.resolveModulePath)
                    ];
                    const summaries = yield this.parser.summarizeModules(allFiles);
                    return JSON.stringify(summaries, null, 1);
                });
            }
        },
        (() => {
            var _b;
            const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create((_b = _classSuper[Symbol.metadata]) !== null && _b !== void 0 ? _b : null) : void 0;
            __run_decorators = [(0, instrumentation_1.instrument)("Tool._run", ["files", "modules"], { attributes: { tool: "CAASTAnalyzerTool" } })];
            __esDecorate(_a, null, __run_decorators, { kind: "method", name: "_run", static: false, private: false, access: { has: obj => "_run" in obj, get: obj => obj._run }, metadata: _metadata }, null, _instanceExtraInitializers);
            if (_metadata) Object.defineProperty(_a, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
        })(),
        _a;
})();
exports.CAASTAnalyzerTool = CAASTAnalyzerTool;
exports.caASTAnalyzerTool = (0, tools_1.tool)({
    name: "ca_analyze_ast",
    description: "Analyze the Abstract Syntax Tree of Python files",
    schema: CAASTAnalyzerToolInputSchema,
    func: (input, runManager) => __awaiter(void 0, void 0, void 0, function* () {
        const tool = new CAASTAnalyzerTool();
        return tool._run(input, runManager);
    })
});
