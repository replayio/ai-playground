import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import { exec } from 'child_process';
import { recordAudio, RecordingResult } from './audio_recording';
import { transcribeAudio, TranscriptionResult } from './audio_transcriber';
import { isError, getErrorMessage } from '../utils/error_handling';

const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);
const execAsync = promisify(exec);

async function playAudio(filePath: string): Promise<void> {
    const absolutePath = path.resolve(filePath);
    const command = `aplay ${absolutePath}`;
    await execAsync(command);
}

async function recordAndTranscribe(duration: number, outputPath: string): Promise<string> {
    const recordingResult = await recordAudio(duration, outputPath);
    if (!recordingResult.success || !recordingResult.filePath) {
        throw new Error(`Recording failed: ${recordingResult.error}`);
    }

    const transcriptionResult = await transcribeAudio(recordingResult.filePath);
    if (!transcriptionResult.success || !transcriptionResult.transcription) {
        throw new Error(`Transcription failed: ${transcriptionResult.error}`);
    }

    return transcriptionResult.transcription;
}

export { playAudio, recordAndTranscribe };

// Main execution
if (require.main === module) {
    (async () => {
        if (process.argv.length !== 4) {
            console.error('Usage: node audio_playground.js <duration_in_seconds> <output_file_path>');
            process.exit(1);
        }

        const [, , durationStr, outputPath] = process.argv;
        const duration = parseInt(durationStr, 10);

        if (isNaN(duration) || duration <= 0) {
            console.error('Error: Duration must be a positive integer.');
            process.exit(1);
        }

        try {
            console.log('Recording audio...');
            const transcription = await recordAndTranscribe(duration, outputPath);
            console.log('Transcription:', transcription);

            console.log('Playing back the recorded audio...');
            await playAudio(outputPath);

            console.log('Audio playground demo completed successfully.');
        } catch (error) {
            console.error('Error:', getErrorMessage(error));
            process.exit(1);
        }
    })();
}
