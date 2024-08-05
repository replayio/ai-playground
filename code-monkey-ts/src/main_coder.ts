import { Coder, runAgentMain } from './agents/agents';

async function main(): Promise<void> {
    await runAgentMain(Coder);
}

if (require.main === module) {
    main().then(() => {
        process.exit(0);
    }).catch((error) => {
        console.error('An error occurred:', error);
        process.exit(1);
    });
}
