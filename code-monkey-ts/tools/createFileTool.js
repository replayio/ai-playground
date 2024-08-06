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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.CreateFileTool = void 0;
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const zod_1 = require("zod");
const ioTool_1 = require("./ioTool");
const utils_1 = require("./utils");
const instrumentation_1 = require("../instrumentation");
const CreateFileToolInputSchema = zod_1.z.object({
    fname: zod_1.z.string().describe("Name of the file to create."),
    content: zod_1.z.string().optional().describe("Initial content of the file (optional).")
});
let CreateFileTool = (() => {
    var _a;
    let _classSuper = ioTool_1.IOTool;
    let _instanceExtraInitializers = [];
    let __call_decorators;
    return _a = class CreateFileTool extends _classSuper {
            constructor() {
                super(...arguments);
                this.name = (__runInitializers(this, _instanceExtraInitializers), "create_file");
                this.description = "Create a new file with optional content";
                this.schema = CreateFileToolInputSchema;
            }
            _call(_b, runManager_1) {
                return __awaiter(this, arguments, void 0, function* ({ fname, content }, runManager) {
                    const filePath = (0, utils_1.makeFilePath)(fname);
                    try {
                        yield fs_1.default.promises.mkdir(path_1.default.dirname(filePath), { recursive: true });
                        yield fs_1.default.promises.writeFile(filePath, content !== null && content !== void 0 ? content : '', { flag: 'wx' });
                        this.notifyFileModified(fname);
                        return `File ${fname} created successfully.`;
                    }
                    catch (error) {
                        console.error(`Failed to create file: ${filePath}`);
                        console.error(error);
                        throw error;
                    }
                });
            }
            notifyFileModified(fname) {
                // Implement the notification logic here
                console.log(`File ${fname} has been modified.`);
            }
        },
        (() => {
            var _b;
            const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create((_b = _classSuper[Symbol.metadata]) !== null && _b !== void 0 ? _b : null) : void 0;
            __call_decorators = [(0, instrumentation_1.instrument)("Tool._run", ["fname", "content"], { attributes: { tool: "CreateFileTool" } })];
            __esDecorate(_a, null, __call_decorators, { kind: "method", name: "_call", static: false, private: false, access: { has: obj => "_call" in obj, get: obj => obj._call }, metadata: _metadata }, null, _instanceExtraInitializers);
            if (_metadata) Object.defineProperty(_a, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
        })(),
        _a;
})();
exports.CreateFileTool = CreateFileTool;
