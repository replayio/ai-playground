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
const path = __importStar(require("path"));
const audio_transcriber_1 = require("../audio_transcriber");
describe('Audio Transcriber', () => {
    let sandbox;
    beforeEach(() => {
        sandbox = sinon.createSandbox();
    });
    afterEach(() => {
        sandbox.restore();
    });
    it('should successfully transcribe audio', () => __awaiter(void 0, void 0, void 0, function* () {
        const testFilePath = path.join(__dirname, 'test_audio.wav');
        const expectedTranscription = 'This is a test transcription';
        // Mock the exec function
        const execStub = sandbox.stub().resolves({
            stdout: expectedTranscription,
            stderr: ''
        });
        sandbox.replace(require('child_process'), 'exec', execStub);
        const result = yield (0, audio_transcriber_1.transcribeAudio)(testFilePath);
        (0, chai_1.expect)(result.success).to.be.true;
        (0, chai_1.expect)(result.transcription).to.equal(expectedTranscription);
        (0, chai_1.expect)(execStub.calledOnce).to.be.true;
        (0, chai_1.expect)(execStub.firstCall.args[0]).to.include(testFilePath);
    }));
    it('should handle transcription errors', () => __awaiter(void 0, void 0, void 0, function* () {
        const testFilePath = path.join(__dirname, 'non_existent_audio.wav');
        const expectedError = 'Transcription failed';
        // Mock the exec function to simulate an error
        const execStub = sandbox.stub().rejects(new Error(expectedError));
        sandbox.replace(require('child_process'), 'exec', execStub);
        const result = yield (0, audio_transcriber_1.transcribeAudio)(testFilePath);
        (0, chai_1.expect)(result.success).to.be.false;
        (0, chai_1.expect)(result.error).to.equal(expectedError);
        (0, chai_1.expect)(execStub.calledOnce).to.be.true;
        (0, chai_1.expect)(execStub.firstCall.args[0]).to.include(testFilePath);
    }));
});
// If you want to run these tests manually, you can use a test runner like Mocha
if (require.main === module) {
    const Mocha = require('mocha');
    const mocha = new Mocha();
    mocha.addFile(__filename);
    mocha.run((failures) => {
        process.exitCode = failures ? 1 : 0;
    });
}
