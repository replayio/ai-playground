"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.instrumentedInvokeAgentTool = exports.invokeAgentTool = exports.InvokeAgentTool = void 0;
var zod_1 = require("zod");
var tools_1 = require("@langchain/core/tools");
var instrumentation_1 = require("../instrumentation");
var service_1 = require("./service");
var InvokeAgentInputSchema = zod_1.z.object({
    agent_name: zod_1.z.string().describe("Name of the agent to invoke"),
    prompt: zod_1.z.string().describe("Prompt to run with the agent")
});
var InvokeAgentTool = /** @class */ (function (_super) {
    __extends(InvokeAgentTool, _super);
    function InvokeAgentTool(fields) {
        var _this = _super.call(this, fields) || this;
        _this.name = "invoke_agent";
        _this.description = "Invokes another agent by name and runs it with a given prompt";
        _this.schema = InvokeAgentInputSchema;
        _this.allowed_agents = (fields === null || fields === void 0 ? void 0 : fields.allowed_agents) || [];
        return _this;
    }
    InvokeAgentTool.prototype._call = function (input, runManager) {
        return __awaiter(this, void 0, void 0, function () {
            var agent_name, prompt, service, response, error_1;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        agent_name = input.agent_name, prompt = input.prompt;
                        if (!this.allowed_agents.includes(agent_name)) {
                            throw new Error("Agent '".concat(agent_name, "' not found or not allowed."));
                        }
                        service = service_1.services_by_agent_name[agent_name];
                        if (!service) {
                            throw new Error("Service for agent '".concat(agent_name, "' not found."));
                        }
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 4, , 5]);
                        // send a prompt, then wait for a response
                        return [4 /*yield*/, service.send_to({ prompt: prompt })];
                    case 2:
                        // send a prompt, then wait for a response
                        _a.sent();
                        return [4 /*yield*/, service.receive_from()];
                    case 3:
                        response = _a.sent();
                        // emit a custom event with the response
                        runManager === null || runManager === void 0 ? void 0 : runManager.handleToolEnd(JSON.stringify(response));
                        return [2 /*return*/, JSON.stringify(response)];
                    case 4:
                        error_1 = _a.sent();
                        console.error("Failed to invoke agent:", agent_name);
                        console.error(error_1);
                        throw error_1;
                    case 5: return [2 /*return*/];
                }
            });
        });
    };
    return InvokeAgentTool;
}(tools_1.Tool));
exports.InvokeAgentTool = InvokeAgentTool;
exports.invokeAgentTool = new InvokeAgentTool();
// Wrapper function to apply the instrumentation decorator
exports.instrumentedInvokeAgentTool = (0, instrumentation_1.instrument)("Tool._call", ["agent_name", "prompt"], { attributes: { tool: "InvokeAgentTool" } })(exports.invokeAgentTool._call.bind(exports.invokeAgentTool));
// You can use the instrumented version like this:
// invokeAgentTool._call = instrumentedInvokeAgentTool;
