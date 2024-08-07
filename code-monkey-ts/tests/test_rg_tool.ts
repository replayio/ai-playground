import { runRipgrep } from '../tools/rg_tool';
import { exec, ExecException } from 'child_process';

jest.mock('child_process');

const mockedExec = exec as jest.MockedFunction<typeof exec>;

describe('runRipgrep', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should return the correct output when matches are found', async () => {
    mockedExec.mockImplementation((command, options, callback) => {
      if (typeof options === 'function') {
        callback = options;
      }
      if (callback) {
        callback(null, 'match1\nmatch2\n', '');
      }
      return {} as any;
    });

    const result = await runRipgrep('pattern', 'path');
    expect(result.success).toBeTruthy();
    expect(result.output).toEqual('match1\nmatch2');
    expect(mockedExec).toHaveBeenCalledTimes(1);
  });

  it('should return an error when the command fails', async () => {
    mockedExec.mockImplementation((command, options, callback) => {
      if (typeof options === 'function') {
        callback = options;
      }
      if (callback) {
        callback(new Error('Command failed') as ExecException, '', 'error');
      }
      return {} as any;
    });

    const result = await runRipgrep('pattern', 'path');
    expect(result.success).toBeFalsy();
    expect(result.error).toEqual('Command failed');
    expect(mockedExec).toHaveBeenCalledTimes(1);
  });

  it('should return an empty output when no matches are found', async () => {
    mockedExec.mockImplementation((command, options, callback) => {
      if (typeof options === 'function') {
        callback = options;
      }
      if (callback) {
        callback(null, '', '');
      }
      return {} as any;
    });

    const result = await runRipgrep('pattern', 'path');
    expect(result.success).toBeTruthy();
    expect(result.output).toEqual('');
    expect(mockedExec).toHaveBeenCalledTimes(1);
  });
});
