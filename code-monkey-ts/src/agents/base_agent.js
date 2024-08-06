"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.BaseAgent = void 0;
class BaseAgent {
    getSystemPrompt() {
        return BaseAgent.SYSTEM_PROMPT;
    }
}
exports.BaseAgent = BaseAgent;
BaseAgent.tools = null;
BaseAgent.SYSTEM_PROMPT = "You don't know what to do. Tell the user that they can't use you and must use an agent with a proper SYSTEM_PROMPT instead.";
