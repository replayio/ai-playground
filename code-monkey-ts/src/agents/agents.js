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
exports.agents = exports.Debugger = exports.Coder = exports.CodeAnalyst = exports.Engineer = exports.EngineeringPlanner = exports.Manager = void 0;
exports.runAgentMain = runAgentMain;
const agent_1 = require("./agent");
const invoke_agent_tool_1 = require("../tools/invoke_agent_tool");
const ask_user_tool_1 = require("../tools/ask_user_tool");
class Manager extends agent_1.Agent {
    setContext(context) {
        this.context = context;
    }
    preparePrompt(prompt) {
        return `
        These are all files: ${this.context.copySrc()}.
        Query: ${prompt.trim()}
        `.trim();
    }
}
exports.Manager = Manager;
Manager.SYSTEM_PROMPT = `
    You are the Manager, an AI designed to manage and coordinate tasks among various agents.
    Your goal is to ensure that tasks are distributed efficiently and completed successfully.
    `;
Manager.tools = [
    invoke_agent_tool_1.invokeAgent,
    ask_user_tool_1.askUser,
];
class EngineeringPlanner extends agent_1.Agent {
}
exports.EngineeringPlanner = EngineeringPlanner;
EngineeringPlanner.SYSTEM_PROMPT = `
    You are the Engineering Planner, responsible for creating high-level plans for software projects.
    `;
EngineeringPlanner.tools = [ask_user_tool_1.askUser];
class Engineer extends agent_1.Agent {
}
exports.Engineer = Engineer;
Engineer.SYSTEM_PROMPT = `
    You are the Engineer, tasked with implementing technical solutions based on the plans provided.
    `;
Engineer.tools = [ask_user_tool_1.askUser];
class CodeAnalyst extends agent_1.Agent {
}
exports.CodeAnalyst = CodeAnalyst;
CodeAnalyst.SYSTEM_PROMPT = `
    You are the Code Analyst, responsible for reviewing and analyzing code for quality and potential improvements.
    `;
CodeAnalyst.tools = [ask_user_tool_1.askUser];
class Coder extends agent_1.Agent {
}
exports.Coder = Coder;
Coder.SYSTEM_PROMPT = `
    You are the Coder, tasked with writing and modifying code based on specifications and requirements.
    `;
Coder.tools = [ask_user_tool_1.askUser];
class Debugger extends agent_1.Agent {
}
exports.Debugger = Debugger;
Debugger.SYSTEM_PROMPT = `
    You are the Debugger, responsible for identifying and fixing issues in the codebase.
    `;
Debugger.tools = [ask_user_tool_1.askUser];
function runAgentImpl(agentClass) {
    return __awaiter(this, void 0, void 0, function* () {
        const agent = new agentClass("default");
        yield agent.runPrompt("");
    });
}
function runAgentMain(agentClass) {
    return __awaiter(this, void 0, void 0, function* () {
        yield runAgentImpl(agentClass);
    });
}
const agents = [Manager, EngineeringPlanner, Engineer, CodeAnalyst, Coder, Debugger];
exports.agents = agents;
