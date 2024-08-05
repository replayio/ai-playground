import * as readline from 'readline';

interface AudioInputResult {
    success: boolean;
    input?: string;
    error?: string;
}

function createReadlineInterface(): readline.Interface {
    return readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });
}

async function getAudioInput(prompt: string): Promise<AudioInputResult> {
    const rl = createReadlineInterface();

    try {
        const input = await new Promise<string>((resolve) => {
            rl.question(prompt, (answer) => {
                resolve(answer.trim());
            });
        });

        return {
            success: true,
            input: input
        };
    } catch (error) {
        return {
            success: false,
            error: error.message
        };
    } finally {
        rl.close();
    }
}

export { getAudioInput, AudioInputResult };

// Main execution
if (require.main === module) {
    (async () => {
        const result = await getAudioInput('Please provide audio input: ');
        
        if (result.success) {
            console.log('Audio input received:', result.input);
        } else {
            console.error('Error:', result.error);
        }
        
        process.exit(result.success ? 0 : 1);
    })();
}
