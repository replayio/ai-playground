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
const agents_1 = require("./agents/agents");
const constants_1 = require("./constants");
const instrumentation_1 = require("./instrumentation");
function main() {
    return __awaiter(this, void 0, void 0, function* () {
        yield (0, agents_1.runAgentMain)(agents_1.Manager);
    });
}
if (require.main === module) {
    (0, constants_1.loadEnvironment)();
    (0, instrumentation_1.initializeTracer)({
        agent: 'Manager',
    });
    main().then(() => {
        process.exit(0);
    }).catch((error) => {
        console.error('An error occurred:', error);
        process.exit(1);
    });
}
