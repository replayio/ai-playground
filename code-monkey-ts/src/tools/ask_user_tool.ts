import * as readline from 'readline';

interface AskUserResult {
    success: boolean;
    response?: string;
    error?: string;
}

async function askUser(question: string): Promise<AskUserResult> {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    return new Promise((resolve) => {
        rl.question(question + ' ', (answer) => {
            rl.close();
            resolve({
                success: true,
                response: answer.trim()
            });
        });
    });
}

export { askUser, AskUserResult };

// Main execution
if (require.main === module) {
    (async () => {
        if (process.argv.length !== 3) {
            console.error('Usage: node ask_user_tool.js "<question>"');
            process.exit(1);
        }

        const [, , question] = process.argv;
        const result = await askUser(question);

        if (result.success) {
            console.log('User response:', result.response);
        } else {
            console.error('Error:', result.error);
        }

        process.exit(result.success ? 0 : 1);
    })();
}
