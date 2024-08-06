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
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const console_1 = require("console");
const simple_term_menu_1 = require("simple-term-menu");
const agents_1 = require("./agents/agents");
const constants_1 = require("./constants");
const instrumentation_1 = require("./instrumentation");
const logs_1 = require("./util/logs");
const console = new console_1.Console({ stdout: process.stdout, stderr: process.stderr });
function main() {
    return __awaiter(this, arguments, void 0, function* (debug = false) {
        (0, logs_1.setupLogging)(debug);
        console.log('\x1b[1m\x1b[32mWelcome to the AI Agent Selector!\x1b[0m');
        const agentChoices = [
            ['Coder', agents_1.Coder],
            ['CodeAnalyst', agents_1.CodeAnalyst],
            ['Manager', agents_1.Manager],
        ];
        const menuItems = agentChoices.map((choice, index) => `${index + 1}. ${choice[0]}`);
        const terminalMenu = new simple_term_menu_1.TerminalMenu(menuItems, { title: 'Choose an agent to run:' });
        const menuEntryIndex = yield terminalMenu.show();
        if (menuEntryIndex === undefined) {
            console.log('\x1b[1m\x1b[31mNo selection made. Exiting...\x1b[0m');
            return;
        }
        const [agentName, AgentClass] = agentChoices[menuEntryIndex];
        console.log(`\x1b[1m\x1b[34mRunning ${agentName} agent...\x1b[0m`);
        const agent = new AgentClass(process.env.AI_MSN);
        agent.initialize();
        // Read prompt from .prompt.md file
        const promptPath = path.join((0, constants_1.getSrcDir)(), '.prompt.md');
        const prompt = fs.readFileSync(promptPath, 'utf-8');
        yield agent.runPrompt(prompt);
        console.log('\x1b[1m\x1b[32mDONE\x1b[0m');
    });
}
if (require.main === module) {
    const args = process.argv.slice(2);
    const debug = args.includes('--debug');
    (0, constants_1.loadEnvironment)();
    (0, instrumentation_1.initializeTracer)({
        agent: 'Coder',
    });
    main(debug).then(() => {
        process.exit(0);
    }).catch((error) => {
        console.error('An error occurred:', error);
        process.exit(1);
    });
}
