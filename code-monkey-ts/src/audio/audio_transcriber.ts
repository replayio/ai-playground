import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import { exec } from 'child_process';

const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);
const execAsync = promisify(exec);

interface TranscriptionResult {
    success: boolean;
    transcription?: string;
    error?: string;
}

async function transcribeAudio(filePath: string): Promise<TranscriptionResult> {
    try {
        const absolutePath = path.resolve(filePath);
        const command = `transcribe-audio "${absolutePath}"`;
        
        const { stdout, stderr } = await execAsync(command);
        
        if (stderr) {
            return {
                success: false,
                error: stderr,
            };
        }
        
        return {
            success: true,
            transcription: stdout.trim(),
        };
    } catch (error) {
        return {
            success: false,
            error: error.message,
        };
    }
}

export { transcribeAudio, TranscriptionResult };

// Main execution
if (require.main === module) {
    (async () => {
        if (process.argv.length !== 3) {
            console.error('Usage: node audio_transcriber.js <file_path>');
            process.exit(1);
        }

        const [, , filePath] = process.argv;
        const result = await transcribeAudio(filePath);
        
        if (result.success) {
            console.log('Transcription:');
            console.log(result.transcription);
        } else {
            console.error('Error:', result.error);
        }
        
        process.exit(result.success ? 0 : 1);
    })();
}
