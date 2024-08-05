import { Coder, runAgentMain } from './agents/agents';

async function main(): Promise<void> {
    await runAgentMain(Coder);
}

if (require.main === module) {
    main().then(() => process.exit(0));
}
