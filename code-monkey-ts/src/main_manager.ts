import { Manager, runAgentMain } from './agents/agents';
import { loadEnvironment } from './constants';
import { initializeTracer } from './instrumentation';

async function main(): Promise<void> {
    await runAgentMain(Manager);
}

if (require.main === module) {
    loadEnvironment();

    initializeTracer({
        agent: 'Manager',
    });

    main().then(() => {
        process.exit(0);
    }).catch((error) => {
        console.error('An error occurred:', error);
        process.exit(1);
    });
}
