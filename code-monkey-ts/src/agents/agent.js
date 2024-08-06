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
var __asyncValues = (this && this.__asyncValues) || function (o) {
    if (!Symbol.asyncIterator) throw new TypeError("Symbol.asyncIterator is not defined.");
    var m = o[Symbol.asyncIterator], i;
    return m ? m.call(o) : (o = typeof __values === "function" ? __values(o) : o[Symbol.iterator](), i = {}, verb("next"), verb("throw"), verb("return"), i[Symbol.asyncIterator] = function () { return this; }, i);
    function verb(n) { i[n] = o[n] && function (v) { return new Promise(function (resolve, reject) { v = o[n](v), settle(resolve, reject, v.done, v.value); }); }; }
    function settle(resolve, reject, d, v) { Promise.resolve(v).then(function(v) { resolve({ value: v, done: d }); }, reject); }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.Agent = void 0;
const base_agent_1 = require("./base_agent");
const msn_1 = require("../models/msn");
const agent_utils_1 = require("../utils/agent_utils");
const sqlite_saver_1 = require("../utils/sqlite_saver");
const message_types_1 = require("../utils/message_types");
const instrument_1 = require("../instrumentation/instrument");
const logger_1 = require("../utils/logger");
let Agent = (() => {
    var _a;
    let _classSuper = base_agent_1.BaseAgent;
    let _instanceExtraInitializers = [];
    let _runPrompt_decorators;
    let _handleCompletion_decorators;
    let _handleModifiedFile_decorators;
    return _a = class Agent extends _classSuper {
            constructor(msnStr) {
                super();
                this.model = __runInitializers(this, _instanceExtraInitializers);
                const msn = msn_1.MSN.fromString(msnStr);
                const memory = new sqlite_saver_1.AsyncSqliteSaver(':memory:');
                this.model = (0, agent_utils_1.createReactAgent)(msn.constructModel(), this.tools, memory);
                this.initialize();
            }
            runPrompt(prompt) {
                return __awaiter(this, void 0, void 0, function* () {
                    var _b, e_1, _c, _d;
                    console.log(`Running prompt: ${prompt}`);
                    const system = new message_types_1.SystemMessage(this.getSystemPrompt());
                    const msg = new message_types_1.HumanMessage(this.preparePrompt(prompt));
                    const modifiedFiles = new Set();
                    try {
                        for (var _e = true, _f = __asyncValues(this.model.streamEvents({ messages: [system, msg] }, this.config, 'v2')), _g; _g = yield _f.next(), _b = _g.done, !_b; _e = true) {
                            _d = _g.value;
                            _e = false;
                            const event = _d;
                            const kind = event.event;
                            logger_1.logger.debug(`Agent received event: ${kind}`);
                        }
                    }
                    catch (e_1_1) { e_1 = { error: e_1_1 }; }
                    finally {
                        try {
                            if (!_e && !_b && (_c = _f.return)) yield _c.call(_f);
                        }
                        finally { if (e_1) throw e_1.error; }
                    }
                    this.handleCompletion(modifiedFiles);
                });
            }
            handleCompletion(modifiedFiles) {
                // Handle completion, show diffs, ask user to apply changes
                // ...
            }
            handleModifiedFile(file) {
                // Handle modified file, show diff, ask user to apply changes
                // ...
            }
        },
        (() => {
            var _b;
            const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create((_b = _classSuper[Symbol.metadata]) !== null && _b !== void 0 ? _b : null) : void 0;
            _runPrompt_decorators = [(0, instrument_1.instrument)('Agent.runPrompt')];
            _handleCompletion_decorators = [(0, instrument_1.instrument)('Agent.handleCompletion')];
            _handleModifiedFile_decorators = [(0, instrument_1.instrument)('Agent.handleModifiedFile')];
            __esDecorate(_a, null, _runPrompt_decorators, { kind: "method", name: "runPrompt", static: false, private: false, access: { has: obj => "runPrompt" in obj, get: obj => obj.runPrompt }, metadata: _metadata }, null, _instanceExtraInitializers);
            __esDecorate(_a, null, _handleCompletion_decorators, { kind: "method", name: "handleCompletion", static: false, private: false, access: { has: obj => "handleCompletion" in obj, get: obj => obj.handleCompletion }, metadata: _metadata }, null, _instanceExtraInitializers);
            __esDecorate(_a, null, _handleModifiedFile_decorators, { kind: "method", name: "handleModifiedFile", static: false, private: false, access: { has: obj => "handleModifiedFile" in obj, get: obj => obj.handleModifiedFile }, metadata: _metadata }, null, _instanceExtraInitializers);
            if (_metadata) Object.defineProperty(_a, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
        })(),
        _a;
})();
exports.Agent = Agent;
