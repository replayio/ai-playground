"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.services_by_agent_name = void 0;
exports.getAgentService = getAgentService;
// Placeholder for service module
exports.services_by_agent_name = {};
// Add any other necessary exports or placeholder functions here
function getAgentService(agentName) {
    return exports.services_by_agent_name[agentName] || null;
}
