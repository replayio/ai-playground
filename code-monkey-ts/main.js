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
exports.main = main;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const commander_1 = require("commander");
const console_1 = require("console");
const agents_1 = require("./agents/agents");
const getSrcDir_1 = require("./getSrcDir");
const instrumentation_1 = require("./instrumentation");
const logs_1 = require("./util/logs");
const console = new console_1.Console({ stdout: process.stdout, stderr: process.stderr });
function main() {
    return __awaiter(this, arguments, void 0, function* (debug = false) {
        (0, logs_1.setupLogging)(debug);
        console.log("\x1b[1m\x1b[32mWelcome to the AI Playground!\x1b[0m");
        console.log("\x1b[1m\x1b[34mRunning Manager agent...\x1b[0m");
        const agent = new agents_1.Manager();
        agent.initialize();
        // Read prompt from .prompt.md file
        const promptPath = path.join((0, getSrcDir_1.getRootDir)(), ".prompt.md");
        const prompt = fs.readFileSync(promptPath, 'utf-8');
        yield agent.runPrompt(prompt);
        console.log("\x1b[1m\x1b[32mDONE\x1b[0m");
    });
}
if (require.main === module) {
    commander_1.program
        .option('--debug', 'Enable debug logging')
        .parse(process.argv);
    const options = commander_1.program.opts();
    (0, getSrcDir_1.loadEnvironment)();
    (0, instrumentation_1.initializeTracer)({
        agent: "Manager",
    });
    main(options.debug)
        .then(() => process.exit(0))
        .catch((error) => {
        console.error(error);
        process.exit(1);
    });
}
