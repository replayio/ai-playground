import { expect } from 'chai';
import * as sinon from 'sinon';
import * as fs from 'fs';
import * as path from 'path';
import { transcribeAudio, TranscriptionResult } from '../audio_transcriber';

describe('Audio Transcriber', () => {
    let sandbox: sinon.SinonSandbox;

    beforeEach(() => {
        sandbox = sinon.createSandbox();
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('should successfully transcribe audio', async () => {
        const testFilePath = path.join(__dirname, 'test_audio.wav');
        const expectedTranscription = 'This is a test transcription';

        // Mock the exec function
        const execStub = sandbox.stub().resolves({
            stdout: expectedTranscription,
            stderr: ''
        });
        sandbox.replace(require('child_process'), 'exec', execStub);

        const result: TranscriptionResult = await transcribeAudio(testFilePath);

        expect(result.success).to.be.true;
        expect(result.transcription).to.equal(expectedTranscription);
        expect(execStub.calledOnce).to.be.true;
        expect(execStub.firstCall.args[0]).to.include(testFilePath);
    });

    it('should handle transcription errors', async () => {
        const testFilePath = path.join(__dirname, 'non_existent_audio.wav');
        const expectedError = 'Transcription failed';

        // Mock the exec function to simulate an error
        const execStub = sandbox.stub().rejects(new Error(expectedError));
        sandbox.replace(require('child_process'), 'exec', execStub);

        const result: TranscriptionResult = await transcribeAudio(testFilePath);

        expect(result.success).to.be.false;
        expect(result.error).to.equal(expectedError);
        expect(execStub.calledOnce).to.be.true;
        expect(execStub.firstCall.args[0]).to.include(testFilePath);
    });
});

// If you want to run these tests manually, you can use a test runner like Mocha
if (require.main === module) {
    const Mocha = require('mocha');
    const mocha = new Mocha();
    mocha.addFile(__filename);
    mocha.run((failures: number) => {
        process.exitCode = failures ? 1 : 0;
    });
}
