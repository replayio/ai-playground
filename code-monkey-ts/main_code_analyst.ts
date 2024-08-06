import { CodeAnalyst, runAgentMain } from './src/agents/agents';

async function main(): Promise<void> {
    await runAgentMain(CodeAnalyst);
}

if (require.main === module) {
    main()
        .then(() => process.exit(0))
        .catch((error) => {
            console.error(error);
            process.exit(1);
        });
}

export { main };
