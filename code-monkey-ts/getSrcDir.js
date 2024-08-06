"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.CLAUDE_RATE_LIMIT = exports.DEFAULT_MSN = void 0;
exports.getSrcDir = getSrcDir;
exports.getRootDir = getRootDir;
exports.getArtifactsDir = getArtifactsDir;
exports.loadEnvironment = loadEnvironment;
exports.getAgentMsn = getAgentMsn;
const path = __importStar(require("path"));
const dotenv = __importStar(require("dotenv"));
function getSrcDir() {
    return path.dirname(__filename);
}
function getRootDir() {
    return path.resolve(path.join(getSrcDir(), "../.."));
}
function getArtifactsDir() {
    return path.resolve(path.join(getRootDir(), "artifacts"));
}
function loadEnvironment() {
    // Load environment variables from .env and .secret.env
    dotenv.config();
    dotenv.config({ path: ".env.secret" });
}
exports.DEFAULT_MSN = "anthropic/claude-3-5-sonnet-20240620/anthropic-beta=max-tokens-3-5-sonnet-2024-07-15";
function getAgentMsn() {
    return process.env.AI_MSN || exports.DEFAULT_MSN;
}
// Claude rate limit
exports.CLAUDE_RATE_LIMIT = 40000; // tokens per minute
