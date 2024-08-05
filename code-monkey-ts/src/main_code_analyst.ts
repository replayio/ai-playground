import { CodeAnalyst, runAgentMain } from './agents/agents';
import { loadEnvironment } from './constants';
import { initializeTracer } from './instrumentation';

async function main(): Promise<void> {
    await runAgentMain(CodeAnalyst);
}

if (require.main === module) {
    loadEnvironment();

    initializeTracer({
        agent: 'CodeAnalyst',
    });

    main().then(() => {
        process.exit(0);
    }).catch((error) => {
        console.error('An error occurred:', error);
        process.exit(1);
    });
}
