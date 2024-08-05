import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import { exec } from 'child_process';

const writeFile = promisify(fs.writeFile);
const execAsync = promisify(exec);

interface RecordingResult {
    success: boolean;
    filePath?: string;
    error?: string;
}

async function recordAudio(duration: number, outputPath: string): Promise<RecordingResult> {
    try {
        const absolutePath = path.resolve(outputPath);
        const command = `arecord -d ${duration} -f cd ${absolutePath}`;
        
        await execAsync(command);
        
        return {
            success: true,
            filePath: absolutePath,
        };
    } catch (error) {
        return {
            success: false,
            error: error.message,
        };
    }
}

export { recordAudio, RecordingResult };

// Main execution
if (require.main === module) {
    (async () => {
        if (process.argv.length !== 4) {
            console.error('Usage: node audio_recording.js <duration_in_seconds> <output_file_path>');
            process.exit(1);
        }

        const [, , durationStr, outputPath] = process.argv;
        const duration = parseInt(durationStr, 10);

        if (isNaN(duration) || duration <= 0) {
            console.error('Error: Duration must be a positive integer.');
            process.exit(1);
        }

        const result = await recordAudio(duration, outputPath);
        
        if (result.success) {
            console.log('Audio recorded successfully.');
            console.log('File saved at:', result.filePath);
        } else {
            console.error('Error:', result.error);
        }
        
        process.exit(result.success ? 0 : 1);
    })();
}
