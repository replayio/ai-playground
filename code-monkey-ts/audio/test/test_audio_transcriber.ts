import * as fs from 'fs';
import * as path from 'path';
import { transcribeAudio, TranscriptionResult } from '../audio_transcriber';
import { exec, ExecException, ExecOptions, ChildProcess } from 'child_process';

jest.mock('child_process');

describe('Audio Transcriber', () => {
    let mockExec: jest.MockedFunction<typeof exec>;

    beforeEach(() => {
        mockExec = exec as jest.MockedFunction<typeof exec>;
        jest.resetAllMocks();
    });

    it('should successfully transcribe audio', async () => {
        const testFilePath = path.join(__dirname, 'test_audio.wav');
        const expectedTranscription = 'This is a test transcription';

        mockExec.mockImplementation((
            command: string,
            options: ExecOptions | null | undefined,
            callback?: ((error: ExecException | null, stdout: string | Buffer, stderr: string | Buffer) => void) | undefined
        ): ChildProcess => {
            if (callback) {
                callback(null, expectedTranscription, '');
            }
            return {} as ChildProcess;
        });

        const result: TranscriptionResult = await transcribeAudio(testFilePath);

        expect(result.success).toBe(true);
        expect(result.transcription).toBe(expectedTranscription);
        expect(mockExec).toHaveBeenCalledTimes(1);
        expect(mockExec.mock.calls[0][0]).toContain(testFilePath);
    });

    it('should handle transcription errors', async () => {
        const testFilePath = path.join(__dirname, 'non_existent_audio.wav');
        const expectedError = 'Transcription failed';

        mockExec.mockImplementation((
            command: string,
            options: ExecOptions | null | undefined,
            callback?: ((error: ExecException | null, stdout: string | Buffer, stderr: string | Buffer) => void) | undefined
        ): ChildProcess => {
            if (callback) {
                callback(new Error(expectedError), '', expectedError);
            }
            return {} as ChildProcess;
        });

        const result: TranscriptionResult = await transcribeAudio(testFilePath);

        expect(result.success).toBe(false);
        expect(result.error).toBe(expectedError);
        expect(mockExec).toHaveBeenCalledTimes(1);
        expect(mockExec.mock.calls[0][0]).toContain(testFilePath);
    });
});
