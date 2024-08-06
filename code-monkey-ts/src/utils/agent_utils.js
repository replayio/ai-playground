"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createReactAgent = createReactAgent;
const agents_1 = require("@langchain/core/agents");
const agents_2 = require("langchain/agents");
function createReactAgent(model, tools, memory) {
    // Create the ReAct agent using LangChain's function
    const agent = (0, agents_2.createReactAgent)({ llm: model, tools });
    // Create and return an AgentExecutor with the agent and memory
    return agents_1.AgentExecutor.fromAgentAndTools({
        agent,
        tools,
        memory,
    });
}
