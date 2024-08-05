import { expect } from 'chai';
import * as sinon from 'sinon';
import { runRipgrep } from '../tools/rg_tool';

describe('runRipgrep', () => {
    let sandbox: sinon.SinonSandbox;

    beforeEach(() => {
        sandbox = sinon.createSandbox();
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('should return the correct output when matches are found', async () => {
        const execStub = sandbox.stub(require('child_process'), 'exec').callsFake((command, callback) => {
            callback(null, { stdout: 'match1\nmatch2\n', stderr: '' });
        });

        const result = await runRipgrep('pattern', 'path');
        expect(result.success).to.be.true;
        expect(result.output).to.equal('match1\nmatch2');
        expect(execStub.calledOnce).to.be.true;
    });

    it('should return an error when the command fails', async () => {
        const execStub = sandbox.stub(require('child_process'), 'exec').callsFake((command, callback) => {
            callback(new Error('Command failed'), { stdout: '', stderr: 'error' });
        });

        const result = await runRipgrep('pattern', 'path');
        expect(result.success).to.be.false;
        expect(result.error).to.equal('Command failed');
        expect(execStub.calledOnce).to.be.true;
    });

    it('should return an empty output when no matches are found', async () => {
        const execStub = sandbox.stub(require('child_process'), 'exec').callsFake((command, callback) => {
            callback(null, { stdout: '', stderr: '' });
        });

        const result = await runRipgrep('pattern', 'path');
        expect(result.success).to.be.true;
        expect(result.output).to.equal('');
        expect(execStub.calledOnce).to.be.true;
    });
});

// Main execution
if (require.main === module) {
    describe('runRipgrep', () => {
        it('should run all tests', () => {
            // This will run all the tests defined above
        });
    });
}
