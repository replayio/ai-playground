import { expect } from 'chai';
import * as sinon from 'sinon';
import { runRipgrep } from '../tools/rg_tool';
import { exec, ExecException, ChildProcess } from 'child_process';

describe('runRipgrep', () => {
    let sandbox: sinon.SinonSandbox;

    beforeEach(() => {
        sandbox = sinon.createSandbox();
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('should return the correct output when matches are found', async () => {
        const execStub = sandbox.stub(exec);
        execStub.yields(null, 'match1\nmatch2\n', '');

        const result = await runRipgrep('pattern', 'path');
        expect(result.success).to.be.true;
        expect(result.output).to.equal('match1\nmatch2');
        expect(execStub.calledOnce).to.be.true;
    });

    it('should return an error when the command fails', async () => {
        const execStub = sandbox.stub(exec);
        execStub.yields(new Error('Command failed'), '', 'error');

        const result = await runRipgrep('pattern', 'path');
        expect(result.success).to.be.false;
        expect(result.error).to.equal('Command failed');
        expect(execStub.calledOnce).to.be.true;
    });

    it('should return an empty output when no matches are found', async () => {
        const execStub = sandbox.stub(exec);
        execStub.yields(null, '', '');

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
