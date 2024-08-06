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
const chai_1 = require("chai");
const sinon = __importStar(require("sinon"));
const rg_tool_1 = require("../tools/rg_tool");
describe('runRipgrep', () => {
    let sandbox;
    beforeEach(() => {
        sandbox = sinon.createSandbox();
    });
    afterEach(() => {
        sandbox.restore();
    });
    it('should return the correct output when matches are found', () => __awaiter(void 0, void 0, void 0, function* () {
        const execStub = sandbox.stub(require('child_process'), 'exec').callsFake((command, callback) => {
            callback(null, { stdout: 'match1\nmatch2\n', stderr: '' });
        });
        const result = yield (0, rg_tool_1.runRipgrep)('pattern', 'path');
        (0, chai_1.expect)(result.success).to.be.true;
        (0, chai_1.expect)(result.output).to.equal('match1\nmatch2');
        (0, chai_1.expect)(execStub.calledOnce).to.be.true;
    }));
    it('should return an error when the command fails', () => __awaiter(void 0, void 0, void 0, function* () {
        const execStub = sandbox.stub(require('child_process'), 'exec').callsFake((command, callback) => {
            callback(new Error('Command failed'), { stdout: '', stderr: 'error' });
        });
        const result = yield (0, rg_tool_1.runRipgrep)('pattern', 'path');
        (0, chai_1.expect)(result.success).to.be.false;
        (0, chai_1.expect)(result.error).to.equal('Command failed');
        (0, chai_1.expect)(execStub.calledOnce).to.be.true;
    }));
    it('should return an empty output when no matches are found', () => __awaiter(void 0, void 0, void 0, function* () {
        const execStub = sandbox.stub(require('child_process'), 'exec').callsFake((command, callback) => {
            callback(null, { stdout: '', stderr: '' });
        });
        const result = yield (0, rg_tool_1.runRipgrep)('pattern', 'path');
        (0, chai_1.expect)(result.success).to.be.true;
        (0, chai_1.expect)(result.output).to.equal('');
        (0, chai_1.expect)(execStub.calledOnce).to.be.true;
    }));
});
// Main execution
if (require.main === module) {
    describe('runRipgrep', () => {
        it('should run all tests', () => {
            // This will run all the tests defined above
        });
    });
}
