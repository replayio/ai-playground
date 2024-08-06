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
exports.replaceInFileTool = exports.ReplaceInFileTool = void 0;
const zod_1 = require("zod");
const tools_1 = require("@langchain/core/tools");
const io_tool_1 = require("./io_tool");
const utils_1 = require("./utils");
const instrumentation_1 = require("../instrumentation");
const ReplaceInFileToolInputSchema = zod_1.z.object({
    fname: zod_1.z.string().describe("Name of the file to edit."),
    to_replace: zod_1.z.string().describe("The string to be replaced."),
    replacement: zod_1.z.string().describe("The string to replace with.")
});
let ReplaceInFileTool = (() => {
    var _a;
    let _classSuper = io_tool_1.IOTool;
    let _instanceExtraInitializers = [];
    let __run_decorators;
    return _a = class ReplaceInFileTool extends _classSuper {
            constructor() {
                super(...arguments);
                this.name = (__runInitializers(this, _instanceExtraInitializers), "replace_in_file");
                this.description = "Replace a specific string in a file with another string";
                this.schema = ReplaceInFileToolInputSchema;
            }
            _run(_b, runManager_1) {
                return __awaiter(this, arguments, void 0, function* ({ fname, to_replace, replacement }, runManager) {
                    const filePath = (0, utils_1.makeFilePath)(fname);
                    const content = yield fs.promises.readFile(filePath, 'utf-8');
                    const occurrences = (content.match(new RegExp(to_replace, 'g')) || []).length;
                    if (occurrences !== 1) {
                        throw new Error(`The string '${to_replace}' appears ${occurrences} times in the file. It must appear exactly once for replacement.`);
                    }
                    const newContent = content.replace(to_replace, replacement);
                    yield fs.promises.writeFile(filePath, newContent, 'utf-8');
                    this.notifyFileModified(fname);
                });
            }
        },
        (() => {
            var _b;
            const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create((_b = _classSuper[Symbol.metadata]) !== null && _b !== void 0 ? _b : null) : void 0;
            __run_decorators = [(0, instrumentation_1.instrument)("Tool._run", ["fname", "to_replace", "replacement"], { attributes: { tool: "ReplaceInFileTool" } })];
            __esDecorate(_a, null, __run_decorators, { kind: "method", name: "_run", static: false, private: false, access: { has: obj => "_run" in obj, get: obj => obj._run }, metadata: _metadata }, null, _instanceExtraInitializers);
            if (_metadata) Object.defineProperty(_a, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
        })(),
        _a;
})();
exports.ReplaceInFileTool = ReplaceInFileTool;
exports.replaceInFileTool = (0, tools_1.tool)({
    name: "replace_in_file",
    description: "Replace a specific string in a file with another string",
    schema: ReplaceInFileToolInputSchema,
    func: (input, runManager) => __awaiter(void 0, void 0, void 0, function* () {
        const tool = new ReplaceInFileTool();
        yield tool._run(input, runManager);
    })
});
